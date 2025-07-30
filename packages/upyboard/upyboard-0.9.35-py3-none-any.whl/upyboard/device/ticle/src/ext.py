import math
import utime
import machine
import ustruct
import rp2
import array
import math

import utools
from . import Dout, Din, Pwm, I2c


class Relay(Dout):
    """
    A class to control multiple relay channels using digital output pins.
    
    This class extends the Dout class to provide relay-specific functionality with
    semantic constants (ON/OFF) for better code readability. It inherits all the
    indexing and slicing capabilities from Dout while adding relay-specific context.
    
    Features:
        - Semantic constants (ON/OFF) for clear relay state control
        - Full inheritance of Dout's indexing and slicing capabilities
        - Multiple relay channel control with single instance
        - Compatible with all Dout operations and methods
        - Better string representation showing relay states
    
    Constants:
        - Relay.ON (1): Relay energized state (closed contact)
        - Relay.OFF (0): Relay de-energized state (open contact)
    
    Example:
        >>> # Single relay control
        >>> pump_relay = Relay([10])
        >>> pump_relay[0] = Relay.ON
        >>> pump_relay[0] = Relay.OFF
        >>> 
        >>> # Multiple relays control
        >>> relays = Relay([10, 11, 12, 13])
        >>> relays[0] = Relay.ON           # Turn on first relay
        >>> relays[1:3] = Relay.OFF        # Turn off relays 1 and 2
        >>> relays[:] = Relay.ON           # Turn on all relays
        >>> 
        >>> # Check relay states
        >>> states = [relays[i] for i in range(len(relays))]
        >>> print(f"Relay states: {states}")
        >>> 
        >>> # Using in conditions
        >>> if relays[0] == Relay.ON:
        ...     print("Pump is running")
        >>> 
        >>> # Relay information
        >>> print(relays)  # Shows: Relay(4 channels, states=[1, 0, 0, 1])
    
    Inheritance:
        This class inherits all methods and properties from Dout, including:
        - Indexing: relay[0], relay[1], etc.
        - Slicing: relay[0:2], relay[:], etc.
        - Assignment: relay[0] = 1, relay[:] = 0, etc.
        - Length: len(relay)
        - Iteration: for state in relay
        - All other Dout functionality
    
    Note:
        While this class uses semantic constants ON/OFF, it's fully compatible
        with numeric values (0 and 1) due to inheritance from Dout.
    """
    ON  = 1
    OFF = 0

    def __init__(self, pins: list[int]|tuple[int, ...]):
        """
        Initialize the relay controller with the specified pins.
        
        This method creates a relay controller that can manage multiple relay
        channels connected to different GPIO pins. Each pin will be configured
        as a digital output pin for controlling relay modules.
        
        :param pins: List or tuple of GPIO pin numbers for relay channels
                    Example: [10, 11, 12] or (10, 11, 12, 13)
        
        :raises TypeError: If pins parameter is not a list or tuple
        :raises ValueError: If no pins are provided
        :raises OSError: If GPIO pin initialization fails
        
        Example:
            >>> # Single relay on pin 10
            >>> pump = Relay([10])
            >>> 
            >>> # Multiple relays on pins 10, 11, 12, 13
            >>> motors = Relay([10, 11, 12, 13])
            >>> 
            >>> # Using tuple instead of list
            >>> lights = Relay((14, 15, 16))
        """
        super().__init__(pins)
    
    def __repr__(self) -> str:
        """
        Return a detailed string representation of the relay controller.
        
        This method provides a human-readable representation showing the number
        of relay channels and their current states, making it easy to debug
        and monitor relay status.
        
        :return: String representation in format "Relay(N channels, states=[...])"
        
        Example:
            >>> relays = Relay([10, 11, 12])
            >>> relays[0] = Relay.ON
            >>> relays[1] = Relay.OFF
            >>> relays[2] = Relay.ON
            >>> print(relays)
            Relay(3 channels, states=[1, 0, 1])
        """
        states = [self[i] for i in range(len(self))]
        return f"Relay({len(self)} channels, states={states})"


class ServoMotor:
    """
    A class to control multiple servo motors using PWM with advanced motion control.
    
    This class provides comprehensive servo motor control with various motion modes including
    linear, easing curves, and custom Bezier curves. It supports both blocking and non-blocking
    operations with precise timing control.
    
    Supported Motion Modes:
        - MODE_LINEAR: Constant speed movement
        - MODE_EASE_IN: Gradual acceleration from rest
        - MODE_EASE_OUT: Gradual deceleration to rest  
        - MODE_EASE_IN_OUT: S-curve with acceleration then deceleration
        - MODE_SINE: Smooth sinusoidal movement
        - MODE_BEZIER: Custom curve with user-defined control points
    
    Example:
        >>> servo = ServoMotor((10, 11), freq=50, min_us=500, max_us=2500)
        >>> servo[0].nonblocking = True
        >>> servo[0].duration_ms = 3000
        >>> servo[0].motion_mode = ServoMotor.MODE_EASE_IN_OUT
        >>> servo[0].angle = 180
        >>> servo[0].wait_for_completion()
        >>> servo.deinit()
    """
    
    # Motion mode constants
    MODE_LINEAR = 0      # Linear movement
    MODE_EASE_IN = 1     # Acceleration from rest
    MODE_EASE_OUT = 2    # Deceleration to rest
    MODE_EASE_IN_OUT = 3 # Acceleration then deceleration (S-curve)
    MODE_SINE = 4        # Sine curve movement
    MODE_BEZIER = 5      # Custom Bezier curve

    def __init__(self, pins: tuple[int, ...], freq: int = 50, min_us: int = 500, max_us: int = 2500, init_angle: float = 0.0):
        """
        Initialize the servo motor controller with the specified pins and parameters.
        
        :param pins: Tuple of GPIO pin numbers for servo motors (e.g., (10, 11, 12))
        :param freq: PWM frequency in Hz (default: 50Hz, standard for servos)
        :param min_us: Minimum pulse width in microseconds for 0° position (default: 500us)
        :param max_us: Maximum pulse width in microseconds for 180° position (default: 2500us)
        :param init_angle: Initial angle for all servos in degrees (default: 0.0°, range: 0-180)
        
        :raises ValueError: If init_angle is outside the valid range (0-180 degrees)
        :raises OSError: If PWM initialization fails
        
        Example:
            >>> # Single servo on pin 10
            >>> servo = ServoMotor((10,))
            >>> 
            >>> # Multiple servos with custom pulse widths
            >>> servos = ServoMotor((10, 11, 12), min_us=600, max_us=2400, init_angle=90)
        """
        if not (0.0 <= init_angle <= 180.0):
            raise ValueError("init_angle must be between 0.0 and 180.0 degrees")
            
        try:
            self._pwm = Pwm(pins)
            self._pwm.freq = freq
        except Exception as e:
            raise OSError(f"Failed to initialize PWM: {e}")
        
        n = len(pins)
        
        # Servo configuration
        self._min_us = [min_us] * n
        self._max_us = [max_us] * n
        init_deg = utools.clamp(init_angle, 0.0, 180.0)
        
        # Current state tracking
        self._current_angles = [init_deg] * n
        self._target_angles = [init_deg] * n
        self._start_angles = [init_deg] * n
        self._start_time = [0] * n
        self._is_moving = [False] * n

        # Motion control parameters
        self._speed_ms = [20] * n                    # Timer period (ms) - for internal use
        self._nonblocking = [False] * n              # Non-blocking mode flag
        self._motion_mode = [self.MODE_LINEAR] * n   # Movement mode
        self._duration_ms = [1000] * n               # Total movement time (ms)
        self._acceleration = [0.0] * n               # Acceleration (deg/ms²)
        self._max_speed = [90.0] * n                 # Maximum speed (deg/ms)

        # Bezier curve control points
        self._bezier_cp1 = [0.25] * n
        self._bezier_cp2 = [0.75] * n
        
        # Timer for non-blocking operations
        self._timer = machine.Timer()
        self._timer_active = False
        
        # Initialize servo positions
        for i in range(n):
            us = self.__compute_us(init_deg, i)
            self._pwm[i].duty_us = int(us)
        
        self._is_shutting_down = False
        
    def __getitem__(self, idx: int|slice) -> "_ServoMotorView":
        """
        Get a view of specific servo(s) for individual control.
        
        :param idx: Index (int) or slice object for servo selection
        :return: A ServoMotorView instance for the selected servo(s)
        
        Example:
            >>> servos = ServoMotor((10, 11, 12))
            >>> servo0 = servos[0]          # First servo
            >>> servo_pair = servos[0:2]    # First two servos
        """
        if isinstance(idx, slice):
            indices = list(range(*idx.indices(len(self._current_angles))))
            return ServoMotor._ServoMotorView(self, indices)
        else:
            return ServoMotor._ServoMotorView(self, [idx])

    def __len__(self) -> int:
        """
        Get the number of servo motors controlled by this instance.
        
        :return: Number of servo motors
        """
        return len(self._current_angles)
    
    def move_to(self, idx: int, target_deg: float, duration_ms: int = None, mode: int = None, accel: float = None):
        """
        Move a specific servo to the target angle with optional parameter overrides.
        
        :param idx: Index of the servo to move (0 to len(servos)-1)
        :param target_deg: Target angle in degrees (0-180)
        :param duration_ms: Movement duration in milliseconds (optional override)
        :param mode: Motion mode (optional override, use MODE_* constants)
        :param accel: Acceleration value (optional override, for MODE_LINEAR with acceleration)
        
        :raises IndexError: If idx is out of range
        :raises ValueError: If target_deg is outside valid range
        
        Example:
            >>> servo.move_to(0, 90, duration_ms=2000, mode=ServoMotor.MODE_EASE_IN_OUT)
        """
        if not (0 <= idx < len(self._current_angles)):
            raise IndexError("Servo index out of range")
        if not (0.0 <= target_deg <= 180.0):
            raise ValueError("target_deg must be between 0.0 and 180.0 degrees")
            
        if duration_ms is not None:
            self._duration_ms[idx] = int(duration_ms)
        if mode is not None:
            if not (0 <= mode <= 5):
                raise ValueError("Invalid motion mode")
            self._motion_mode[idx] = mode
        if accel is not None:
            self._acceleration[idx] = float(accel)
        
        self._set_target(idx, target_deg)

    def stop_all(self):
        """
        Stop all servo movements immediately and disable the timer.
        
        This method immediately halts all servo movements by setting their target angles
        to their current positions and stopping the internal timer.
        
        Example:
            >>> servo.stop_all()  # Emergency stop
        """
        try:
            self._is_shutting_down = True
            
            for i in range(len(self._is_moving)):
                self._is_moving[i] = False
                self._target_angles[i] = self._current_angles[i]
            
            if self._timer_active:
                try:
                    utime.sleep_ms(50)
                    self._timer.deinit()
                except Exception:
                    pass
                finally:
                    self._timer_active = False
        except Exception:
            pass

    def wait_for_completion(self, timeout_ms: int = 10000) -> bool:
        """
        Wait for all servo movements to complete or timeout.
        
        :param timeout_ms: Maximum time to wait in milliseconds (default: 10000ms)
        :return: True if all movements completed, False if timeout occurred
        
        Example:
            >>> if servo.wait_for_completion(5000):
            ...     print("All movements completed")
            ... else:
            ...     print("Timeout occurred")
        """
        start_time = utime.ticks_ms()
        while any(self._is_moving):
            if utime.ticks_diff(utime.ticks_ms(), start_time) > timeout_ms:
                return False
            utime.sleep_ms(10)
        return True

    def deinit(self) -> None:
        """
        Deinitialize the servo controller and release resources safely.
        
        This method stops all movements, disables the timer, and releases PWM resources.
        It includes error handling for safe cleanup during interruption.
        """
        try:
            self.stop_all()
            
            utime.sleep_ms(100)
            
            try:
                self._pwm.enable = False
                utime.sleep_ms(20)
                self._pwm.deinit()
            except Exception:
                pass
        except Exception:
            pass
        finally:
            self._is_shutting_down = True
            self._timer_active = False            

    def set_calibration(self, idx: int, min_us: int, max_us: int):
        """
        Set calibration values for a specific servo motor.
        
        Use this method to fine-tune servo positioning for different servo models
        or to correct for mechanical variations.
        
        :param idx: Index of the servo to calibrate (0 to len(servos)-1)
        :param min_us: Minimum pulse width for 0° position in microseconds
        :param max_us: Maximum pulse width for 180° position in microseconds
        
        :raises IndexError: If idx is out of range
        :raises ValueError: If min_us >= max_us or values are unreasonable
        
        Example:
            >>> # Calibrate servo 0 for SG90 micro servo
            >>> servo.set_calibration(0, min_us=600, max_us=2300)
        """
        if not (0 <= idx < len(self._current_angles)):
            raise IndexError("Servo index out of range")
        if min_us >= max_us:
            raise ValueError("min_us must be less than max_us")
        if not (100 <= min_us <= 3000) or not (100 <= max_us <= 3000):
            raise ValueError("Pulse width values must be between 100 and 3000 microseconds")
            
        self._min_us[idx] = min_us
        self._max_us[idx] = max_us

    def set_speed_dps(self, idx: int, degrees_per_second: float):
        """
        Set movement speed in degrees per second for a specific servo.
        
        This method automatically calculates the required duration based on the
        distance to the target angle and the desired speed.
        
        :param idx: Index of the servo (0 to len(servos)-1)
        :param degrees_per_second: Desired speed in degrees per second
        
        :raises IndexError: If idx is out of range
        :raises ValueError: If degrees_per_second is not positive
        
        Example:
            >>> servo.set_speed_dps(0, 30.0)  # 30 degrees per second
        """
        if not (0 <= idx < len(self._current_angles)):
            raise IndexError("Servo index out of range")
        if degrees_per_second <= 0:
            raise ValueError("degrees_per_second must be positive")
            
        current_angle = self._current_angles[idx]
        target_angle = self._target_angles[idx]
        angle_diff = abs(target_angle - current_angle)
        
        if angle_diff > 0:
            required_time_ms = int((angle_diff / degrees_per_second) * 1000)
            self._duration_ms[idx] = max(100, required_time_ms)  # Minimum 100ms

    def set_bezier_control_points(self, cp1: float, cp2: float):
        """
        Set Bezier curve control points for all servos.
        
        Control points define the shape of the Bezier curve used in MODE_BEZIER.
        Values closer to 0 create sharper curves, values closer to 1 create gentler curves.
        
        :param cp1: First control point (0.0 to 1.0)
        :param cp2: Second control point (0.0 to 1.0)
        
        :raises ValueError: If control points are outside valid range
        
        Example:
            >>> servo.set_bezier_control_points(0.1, 0.9)  # Sharp S-curve
            >>> servo.set_bezier_control_points(0.4, 0.6)  # Gentle curve
        """
        if not (0.0 <= cp1 <= 1.0) or not (0.0 <= cp2 <= 1.0):
            raise ValueError("Control points must be between 0.0 and 1.0")
            
        for i in range(len(self._bezier_cp1)):
            self._bezier_cp1[i] = float(cp1)
            self._bezier_cp2[i] = float(cp2)

    @property
    def angle(self) -> list[float]:
        """
        Get or set the current angles of all servo motors.
        
        :return: List of current angles in degrees for each servo
        
        Example:
            >>> angles = servo.angle      # Get all angles
            >>> servo.angle = 90          # Set all servos to 90 degrees
        """
        return self._current_angles[:]

    @angle.setter
    def angle(self, deg: float):
        """Set the target angle for all servo motors."""
        if not (0.0 <= deg <= 180.0):
            raise ValueError("Angle must be between 0.0 and 180.0 degrees")
        for i in range(len(self._current_angles)):
            self._set_target(i, deg)

    @property
    def speed_dps(self) -> list[float]:
        """
        Get the current movement speeds in degrees per second for all servos.
        
        :return: List of speeds in degrees per second for each servo
        """
        speeds = []
        for i in range(len(self._current_angles)):
            angle_diff = abs(self._target_angles[i] - self._current_angles[i])
            duration_s = self._duration_ms[i] / 1000.0
            if duration_s > 0:
                speeds.append(angle_diff / duration_s)
            else:
                speeds.append(0.0)
        return speeds

    @speed_dps.setter
    def speed_dps(self, dps: float):
        """Set movement speed in degrees per second for all servos."""
        if dps <= 0:
            raise ValueError("Speed must be positive")
        for i in range(len(self._current_angles)):
            self.set_speed_dps(i, dps)

    @property
    def duration_ms(self) -> list[int]:
        """
        Get or set the movement duration in milliseconds for all servos.
        
        :return: List of durations in milliseconds for each servo
        
        Example:
            >>> servo.duration_ms = 3000  # 3 second movements
            >>> durations = servo.duration_ms
        """
        return self._duration_ms[:]

    @duration_ms.setter
    def duration_ms(self, ms: int):
        """Set movement duration in milliseconds for all servos."""
        if ms <= 0:
            raise ValueError("Duration must be positive")
        ms = int(ms)
        for i in range(len(self._duration_ms)):
            self._duration_ms[i] = ms

    @property
    def motion_mode(self) -> list[int]:
        """
        Get or set the motion mode for all servos.
        
        :return: List of motion modes for each servo (use MODE_* constants)
        
        Available modes:
            - MODE_LINEAR (0): Constant speed
            - MODE_EASE_IN (1): Gradual acceleration
            - MODE_EASE_OUT (2): Gradual deceleration
            - MODE_EASE_IN_OUT (3): S-curve movement
            - MODE_SINE (4): Sinusoidal movement
            - MODE_BEZIER (5): Custom Bezier curve
        """
        return self._motion_mode[:]

    @motion_mode.setter
    def motion_mode(self, mode: int):
        """Set motion mode for all servos."""
        if not (0 <= mode <= 5):
            raise ValueError("Invalid motion mode. Use MODE_* constants (0-5)")
        for i in range(len(self._motion_mode)):
            self._motion_mode[i] = mode

    @property
    def acceleration(self) -> list[float]:
        """
        Get or set acceleration values for all servos (used with MODE_LINEAR).
        
        :return: List of acceleration values in degrees/ms² for each servo
        """
        return self._acceleration[:]

    @acceleration.setter
    def acceleration(self, accel: float):
        """Set acceleration for all servos."""
        accel = float(accel)
        for i in range(len(self._acceleration)):
            self._acceleration[i] = accel

    @property
    def max_speed(self) -> list[float]:
        """
        Get or set maximum speed values for all servos (used with acceleration).
        
        :return: List of maximum speeds in degrees/ms for each servo
        """
        return self._max_speed[:]

    @max_speed.setter
    def max_speed(self, speed: float):
        """Set maximum speed for all servos."""
        if speed <= 0:
            raise ValueError("Maximum speed must be positive")
        speed = float(speed)
        for i in range(len(self._max_speed)):
            self._max_speed[i] = speed

    @property
    def nonblocking(self) -> list[bool]:
        """
        Get or set non-blocking mode for all servos.
        
        :return: List of non-blocking flags for each servo
        
        When non-blocking is True, servo movements run in the background using a timer.
        When False, movements are immediate and blocking.
        """
        return self._nonblocking[:]

    @nonblocking.setter
    def nonblocking(self, flag: bool):
        """Set non-blocking mode for all servos."""
        flag = bool(flag)
        for i in range(len(self._nonblocking)):
            self._nonblocking[i] = flag

    @property
    def is_moving(self) -> list[bool]:
        """
        Get the movement status of all servos.
        
        :return: List of boolean values indicating if each servo is currently moving
        
        Example:
            >>> if any(servo.is_moving):
            ...     print("Some servos are still moving")
        """
        return self._is_moving[:]

    @property
    def speed_ms(self) -> list[int]:
        """
        Get or set timer period in milliseconds (internal use, prefer duration_ms).
        
        :return: List of timer periods in milliseconds for each servo
        """
        return self._speed_ms[:]

    @speed_ms.setter
    def speed_ms(self, ms: int):
        """Set timer period in milliseconds (internal use, prefer duration_ms)."""
        ms = int(ms)
        for i in range(len(self._speed_ms)):
            self._speed_ms[i] = ms

    def __compute_us(self, deg: float, idx: int) -> float:
        """
        Convert angle to pulse width in microseconds for a specific servo.
        
        :param deg: Angle in degrees (0-180)
        :param idx: Servo index
        :return: Pulse width in microseconds
        """
        deg = utools.clamp(deg, 0.0, 180.0)
        span = self._max_us[idx] - self._min_us[idx]
        us = self._min_us[idx] + span * deg / 180.0
        return us

    def __ease_in_out(self, t: float) -> float:
        """Apply ease-in-out curve (smooth S-curve)."""
        return (1 - math.cos(t * math.pi)) / 2

    def __ease_in(self, t: float) -> float:
        """Apply ease-in curve (gradual acceleration)."""
        return t * t

    def __ease_out(self, t: float) -> float:
        """Apply ease-out curve (gradual deceleration)."""
        return 1.0 - (1.0 - t) * (1.0 - t)

    def __sine_curve(self, t: float) -> float:
        """Apply sine curve (smooth sinusoidal movement)."""
        return (1.0 - math.cos(t * math.pi)) / 2.0

    def __bezier_curve(self, t: float, cp1: float, cp2: float) -> float:
        """Apply cubic Bezier curve with control points."""
        u = 1.0 - t
        return 3 * u * u * t * cp1 + 3 * u * t * t * cp2 + t * t * t

    def __linear_with_acceleration(self, idx: int, elapsed_ms: float) -> float:
        """Calculate progress with acceleration profile."""
        accel = self._acceleration[idx]
        max_speed = self._max_speed[idx]
        total_distance = abs(self._target_angles[idx] - self._start_angles[idx])
        
        if total_distance == 0:
            return 1.0
        
        if accel <= 0:
            duration_ms = self._duration_ms[idx]
            return min(elapsed_ms / duration_ms, 1.0) if duration_ms > 0 else 1.0
        
        # Acceleration profile calculation
        accel_time = max_speed / accel
        accel_distance = 0.5 * accel * accel_time * accel_time
        
        if total_distance <= 2 * accel_distance:
            # Triangular velocity profile
            peak_time = math.sqrt(total_distance / accel)
            if elapsed_ms <= peak_time:
                distance = 0.5 * accel * elapsed_ms * elapsed_ms
            else:
                decel_time = elapsed_ms - peak_time
                distance = accel_distance - 0.5 * accel * decel_time * decel_time
        else:
            # Trapezoidal velocity profile
            const_distance = total_distance - 2 * accel_distance
            const_time = const_distance / max_speed
            decel_start_time = accel_time + const_time
            
            if elapsed_ms <= accel_time:
                distance = 0.5 * accel * elapsed_ms * elapsed_ms
            elif elapsed_ms <= decel_start_time:
                distance = accel_distance + max_speed * (elapsed_ms - accel_time)
            else:
                decel_time = elapsed_ms - decel_start_time
                distance = accel_distance + const_distance + max_speed * decel_time - 0.5 * accel * decel_time * decel_time
        
        progress = distance / total_distance
        return max(0.0, min(progress, 1.0))

    def __calculate_angle(self, idx: int, elapsed_ms: float, duration_ms: float) -> float:
        """Calculate current angle based on motion mode and elapsed time."""
        if duration_ms <= 0:
            return self._target_angles[idx]
        
        start_angle = self._start_angles[idx]
        target_angle = self._target_angles[idx]
        angle_diff = target_angle - start_angle
        
        if abs(angle_diff) < 0.01:
            return target_angle
        
        # Calculate base progress (0.0 to 1.0)
        progress = min(elapsed_ms / duration_ms, 1.0)
        
        # Apply motion curve
        mode = self._motion_mode[idx]
        if mode == self.MODE_LINEAR:
            if self._acceleration[idx] > 0:
                curve_progress = self.__linear_with_acceleration(idx, elapsed_ms)
            else:
                curve_progress = progress
        elif mode == self.MODE_EASE_IN:
            curve_progress = self.__ease_in(progress)
        elif mode == self.MODE_EASE_OUT:
            curve_progress = self.__ease_out(progress)
        elif mode == self.MODE_EASE_IN_OUT:
            curve_progress = self.__ease_in_out(progress)
        elif mode == self.MODE_SINE:
            curve_progress = self.__sine_curve(progress)
        elif mode == self.MODE_BEZIER:
            curve_progress = self.__bezier_curve(progress, self._bezier_cp1[idx], self._bezier_cp2[idx])
        else:
            curve_progress = progress
        
        # Ensure progress stays within bounds
        curve_progress = max(0.0, min(curve_progress, 1.0))
        calculated_angle = start_angle + angle_diff * curve_progress
        
        # Final bounds checking
        if angle_diff >= 0:
            calculated_angle = min(calculated_angle, target_angle)
        else:
            calculated_angle = max(calculated_angle, target_angle)
        
        return calculated_angle

    def __calculate_optimal_timer_period(self) -> int:
        """Calculate optimal timer period based on active servo movements."""
        moving_servos = [i for i in range(len(self._is_moving)) 
                        if self._nonblocking[i] and self._is_moving[i]]
        
        if not moving_servos:
            return 20 
        
        min_duration = min(self._duration_ms[i] for i in moving_servos)
        optimal_period = max(5, min(10, min_duration // 500))
        
        return optimal_period

    def _set_target(self, idx: int, deg: float) -> None:
        """Set target angle for a specific servo and start movement if needed."""
        deg = utools.clamp(deg, 0.0, 180.0)
        self._target_angles[idx] = deg
        self._start_angles[idx] = self._current_angles[idx]
        
        if not self._nonblocking[idx]:
            # Blocking mode - immediate movement
            us = self.__compute_us(deg, idx)
            self._pwm[idx].duty_us = int(us)
            self._current_angles[idx] = deg
            self._is_moving[idx] = False
        else:
            # Non-blocking mode - timer-based movement
            self._start_time[idx] = utime.ticks_ms()
            self._is_moving[idx] = True
            
            if not self._timer_active:
                optimal_period = self.__calculate_optimal_timer_period()
                self._timer.init(
                    period=optimal_period,
                    mode=machine.Timer.PERIODIC,
                    callback=self.__timer_cb
                )
                self._timer_active = True

    def __timer_cb(self, t) -> None:
        """Timer callback for non-blocking servo movements."""
        any_moving = False
        
        if self._is_shutting_down:
            return
        
        current_time = utime.ticks_ms()
        
        for idx in range(len(self._current_angles)):
            if not self._nonblocking[idx] or not self._is_moving[idx]:
                continue
            
            elapsed_ms = utime.ticks_diff(current_time, self._start_time[idx])
            duration_ms = self._duration_ms[idx]
            target_angle = self._target_angles[idx]
            
            # Check completion conditions
            time_completed = elapsed_ms >= duration_ms
            angle_reached = abs(self._current_angles[idx] - target_angle) <= 0.1
            progress = elapsed_ms / duration_ms
            near_completion = progress >= 0.99
            
            if time_completed or (angle_reached and near_completion):
                # Movement completed
                self._current_angles[idx] = target_angle
                self._is_moving[idx] = False
                us = self.__compute_us(target_angle, idx)
                self._pwm[idx].duty_us = int(round(us))
                continue
            
            # Calculate and apply intermediate position
            new_angle = self.__calculate_angle(idx, elapsed_ms, duration_ms)
            
            if abs(new_angle - self._current_angles[idx]) >= 0.01:
                self._current_angles[idx] = new_angle
                us = self.__compute_us(new_angle, idx)
                self._pwm[idx].duty_us = int(round(us))
            
            any_moving = True
        
        # Stop timer if no servos are moving
        if not any_moving:
            self._timer.deinit()
            self._timer_active = False

    class _ServoMotorView:
        """
        A view class for controlling individual servos or groups of servos.
        
        This class provides the same interface as ServoMotor but operates on
        a subset of servos. It's returned by ServoMotor.__getitem__().
        """

        def __init__(self, parent: "ServoMotor", indices: list):
            """Initialize servo view with parent reference and servo indices."""
            self.__parent = parent
            self.__indices = indices

        def __getitem__(self, idx: int|slice) -> "ServoMotor._ServoMotorView":
            """Get a sub-view of this view."""
            if isinstance(idx, slice):
                selected_indices = [self.__indices[i] for i in range(*idx.indices(len(self.__indices)))]
                return ServoMotor._ServoMotorView(self.__parent, selected_indices)
            else:
                return ServoMotor._ServoMotorView(self.__parent, [self.__indices[idx]])

        def __len__(self) -> int:
            """Get the number of servos in this view."""
            return len(self.__indices)

        # Mirror all properties and methods from parent class
        @property
        def angle(self) -> list[float]:
            """Get current angles of servos in this view."""
            return [self.__parent._current_angles[i] for i in self.__indices]

        @angle.setter
        def angle(self, deg: float):
            """Set target angle for all servos in this view."""
            if not (0.0 <= deg <= 180.0):
                raise ValueError("Angle must be between 0.0 and 180.0 degrees")
            for i in self.__indices:
                self.__parent._set_target(i, deg)

        @property
        def duration_ms(self) -> list[int]:
            """Get movement duration for servos in this view."""
            return [self.__parent._duration_ms[i] for i in self.__indices]

        @duration_ms.setter
        def duration_ms(self, ms: int):
            """Set movement duration for servos in this view."""
            if ms <= 0:
                raise ValueError("Duration must be positive")
            ms = int(ms)
            for i in self.__indices:
                self.__parent._duration_ms[i] = ms

        @property
        def motion_mode(self) -> list[int]:
            """Get motion mode for servos in this view."""
            return [self.__parent._motion_mode[i] for i in self.__indices]

        @motion_mode.setter
        def motion_mode(self, mode: int):
            """Set motion mode for servos in this view."""
            if not (0 <= mode <= 5):
                raise ValueError("Invalid motion mode. Use MODE_* constants (0-5)")
            for i in self.__indices:
                self.__parent._motion_mode[i] = mode

        @property
        def nonblocking(self) -> list[bool]:
            """Get non-blocking mode for servos in this view."""
            return [self.__parent._nonblocking[i] for i in self.__indices]

        @nonblocking.setter
        def nonblocking(self, flag: bool):
            """Set non-blocking mode for servos in this view."""
            flag = bool(flag)
            for i in self.__indices:
                self.__parent._nonblocking[i] = flag

        @property
        def is_moving(self) -> list[bool]:
            """Get movement status for servos in this view."""
            return [self.__parent._is_moving[i] for i in self.__indices]

        @property
        def acceleration(self) -> list[float]:
            """Get acceleration values for servos in this view."""
            return [self.__parent._acceleration[i] for i in self.__indices]

        @acceleration.setter
        def acceleration(self, accel: float):
            """Set acceleration for servos in this view."""
            accel = float(accel)
            for i in self.__indices:
                self.__parent._acceleration[i] = accel

        @property
        def max_speed(self) -> list[float]:
            """Get maximum speed values for servos in this view."""
            return [self.__parent._max_speed[i] for i in self.__indices]

        @max_speed.setter
        def max_speed(self, speed: float):
            """Set maximum speed for servos in this view."""
            if speed <= 0:
                raise ValueError("Maximum speed must be positive")
            speed = float(speed)
            for i in self.__indices:
                self.__parent._max_speed[i] = speed

        @property
        def speed_ms(self) -> list[int]:
            """Get timer period for servos in this view."""
            return [self.__parent._speed_ms[i] for i in self.__indices]

        @speed_ms.setter
        def speed_ms(self, ms: int):
            """Set timer period for servos in this view."""
            ms = int(ms)
            for i in self.__indices:
                self.__parent._speed_ms[i] = ms

        @property
        def speed_dps(self) -> list[float]:
            """Get movement speeds in degrees per second for servos in this view."""
            parent_speeds = self.__parent.speed_dps
            return [parent_speeds[i] for i in self.__indices]

        @speed_dps.setter
        def speed_dps(self, dps: float):
            """Set movement speed in degrees per second for servos in this view."""
            if dps <= 0:
                raise ValueError("Speed must be positive")
            for i in self.__indices:
                self.__parent.set_speed_dps(i, dps)

        def move_to(self, target_deg: float, duration_ms: int = None, mode: int = None, accel: float = None):
            """Move all servos in this view to the target angle."""
            if not (0.0 <= target_deg <= 180.0):
                raise ValueError("target_deg must be between 0.0 and 180.0 degrees")
            for i in self.__indices:
                self.__parent.move_to(i, target_deg, duration_ms, mode, accel)

        def set_calibration(self, min_us: int, max_us: int):
            """Set calibration for all servos in this view."""
            if min_us >= max_us:
                raise ValueError("min_us must be less than max_us")
            for i in self.__indices:
                self.__parent.set_calibration(i, min_us, max_us)

        def set_bezier_control_points(self, cp1: float, cp2: float):
            """Set Bezier control points for all servos in this view."""
            if not (0.0 <= cp1 <= 1.0) or not (0.0 <= cp2 <= 1.0):
                raise ValueError("Control points must be between 0.0 and 1.0")
            for i in self.__indices:
                self.__parent._bezier_cp1[i] = float(cp1)
                self.__parent._bezier_cp2[i] = float(cp2)

        def wait_for_completion(self, timeout_ms: int = 10000) -> bool:
            """Wait for all servos in this view to complete their movements."""
            start_time = utime.ticks_ms()
            while any(self.__parent._is_moving[i] for i in self.__indices):
                if utime.ticks_diff(utime.ticks_ms(), start_time) > timeout_ms:
                    return False
                utime.sleep_ms(10)
            return True

        def stop(self):
            """Stop all servos in this view."""
            for i in self.__indices:
                self.__parent._is_moving[i] = False
                self.__parent._target_angles[i] = self.__parent._current_angles[i]


class SR04:
    """
    Multi-channel HC-SR04 ultrasonic distance sensor controller with Kalman filtering.
    
    Features:
        - Multiple sensor support with individual configuration
        - Distance measurement from 2cm to 400cm per sensor
        - Temperature compensation for speed of sound
        - Individual Kalman filters for noise reduction per sensor
        - Blocking and non-blocking measurement modes with user callbacks
        - Configurable measurement and process noise per sensor
        - Timeout protection for failed measurements
        - Unified indexing/slicing and property-based interface
    
    Example:
        >>> def my_callback(pin, distance):
        ...     print(f"Sensor {pin}: {distance}cm")
        >>> 
        >>> u = SR04([(1, 2), (3, 4), (5, 6), (7, 8)])
        >>> 
        >>> # Direct reading via indexing/slicing
        >>> print(u[:])              # Read all sensors
        >>> print(u[::2])            # Read even sensors (0, 2)
        >>> print(u[1::2])           # Read odd sensors (1, 3)
        >>> 
        >>> # Configuration via indexing/slicing + properties
        >>> u[:].nonblocking = True               # All sensors non-blocking
        >>> u[::2].callback = my_callback         # Even sensors callback
        >>> u[:].filter = {'Q': 1.0, 'R': 0.3}   # All sensors filter
        >>> u[1::2].temperature = 25.0            # Odd sensors temperature
        >>> 
        >>> # Start non-blocking measurements
        >>> u.measurement = True
    """
    
    def __init__(self, sensor_configs: list[tuple[int, int]], *, temp_c: float = 20.0, R: float = 25.0, Q: float = 4.0, period_ms: int = 100):
        """
        Initialize multiple HC-SR04 ultrasonic sensors.
        :param sensor_configs: List of tuples (trig_pin, echo_pin) for each sensor
        :param temp_c: Temperature in degrees Celsius for speed of sound calculation (default: 20.0)
        :param R: Measurement noise covariance (default: 25.0)
        :param Q: Process noise covariance (default: 4.0)
        :param period_ms: Measurement period in milliseconds (default: 100)
        """
        if not sensor_configs:
            raise ValueError("At least one sensor configuration must be provided")
        
        if not (-40.0 <= temp_c <= 85.0):
            raise ValueError("Temperature must be between -40°C and +85°C")
        
        n = len(sensor_configs)
        
        try:
            # Initialize GPIO pins for all sensors
            trig_pins = [config[0] for config in sensor_configs]
            echo_pins = [config[1] for config in sensor_configs]
            
            self._trig = Dout(trig_pins)
            self._echo = Din(echo_pins)
        except Exception as e:
            raise OSError(f"Failed to initialize GPIO pins: {e}")
        
        # Store pin configurations for callback identification
        self._trig_pins = trig_pins
        self._echo_pins = echo_pins
        
        # Kalman filter state variables for each sensor
        self._x = [0.0] * n          # Position estimates
        self._v = [0.0] * n          # Velocity estimates  
        self._P = [[[1.0, 0.0], [0.0, 1.0]] for _ in range(n)]  # Error covariance matrices
        self._R = [float(R)] * n     # Measurement noise covariances
        self._Q = [float(Q)] * n     # Process noise covariances
        
        # Environmental and control parameters
        self._temp_c = [float(temp_c)] * n
        self._nonblocking = [False] * n
        
        # Non-blocking measurement state
        self._measurement_active = [False] * n
        self._measurement_start_time = [0] * n
        
        # Callback configuration - per sensor
        self._user_callbacks = [None] * n
        self._period_ms = max(10, period_ms)
        self._measurement_enabled = False
        
        # Timer for non-blocking operations
        self._timer = machine.Timer()
        self._timer_active = False
        
        # Initialize triggers to LOW
        for i in range(n):
            self._trig[i] = 0

    def __getitem__(self, idx: int|slice) -> "_SR04View":
        """
        Get a view for specific sensor(s) that supports both reading and configuration.
        
        :param idx: Index or slice of sensors to access
        :return: SR04._SR04View instance for the specified sensors
        """
        if isinstance(idx, slice):
            indices = list(range(*idx.indices(len(self._temp_c))))
            return SR04._SR04View(self, indices)
        elif isinstance(idx, int):
            if not (0 <= idx < len(self._temp_c)):
                raise IndexError("Sensor index out of range")
            return SR04._SR04View(self, [idx])
        else:
            raise TypeError("Index must be int or slice")

    def __len__(self) -> int:
        """
        Get the number of sensors controlled by this instance.
        
        :return: Number of sensors initialized
        """
        return len(self._temp_c)

    def __repr__(self) -> str:
        """
        Return a string representation of the SR04 sensor controller.
        
        :return: String representation of the SR04 instance
        """
        nb_count = sum(self._nonblocking)
        cb_count = sum(1 for cb in self._user_callbacks if cb is not None)
        return (f"SR04({len(self)} sensors, {nb_count} non-blocking, {cb_count} with callbacks)")

    def _cm_per_us(self, temp: float) -> float:
        """
        Calculate the speed of sound in cm/µs based on temperature.
        
        :param temp: Temperature in degrees Celsius
        :return: Speed of sound in cm/us
        """
        speed_ms = 331.3 + 0.606 * temp  # Speed in m/s
        speed_cm_us = (speed_ms * 100.0) / 1_000_000  # Convert to cm/µs
        return speed_cm_us / 2.0  # Divide by 2 for round-trip

    def _trigger(self, idx: int):
        """
        Send a 10us trigger pulse to a specific sensor.
        
        :param idx: Index of the sensor to trigger
        """
        self._trig[idx] = 0  # Ensure clean LOW state
        utime.sleep_us(2)    # Brief settling time
        self._trig[idx] = 1  # Set HIGH
        utime.sleep_us(10)   # 10us trigger pulse
        self._trig[idx] = 0  # Return to LOW

    def _kalman1d(self, idx: int, z: float, dt: float = 0.06) -> float:
        """
        1D Kalman filter for distance measurement smoothing for a specific sensor.
        
        :param idx: Index of the sensor to apply Kalman filter
        :param z: Measured distance (raw sensor reading)
        :param dt: Time step in seconds (default: 0.06)
        :return: Filtered distance estimate
        """
        # Prediction step
        self._x[idx] += self._v[idx] * dt
        P = self._P[idx]
        P[0][0] += dt * (2 * P[1][0] + dt * P[1][1]) + self._Q[idx]
        P[0][1] += dt * P[1][1]
        P[1][0] += dt * P[1][1]

        # Update step
        innovation = z - self._x[idx]  # Measurement residual
        S = P[0][0] + self._R[idx]     # Innovation covariance
        K0 = P[0][0] / S               # Kalman gain for position
        K1 = P[1][0] / S               # Kalman gain for velocity

        # State update
        self._x[idx] += K0 * innovation
        self._v[idx] += K1 * innovation

        # Covariance update
        P[0][0] -= K0 * P[0][0]
        P[0][1] -= K0 * P[0][1]
        P[1][0] -= K1 * P[0][0]
        P[1][1] -= K1 * P[0][1]

        return self._x[idx]

    def _safe_call_callback(self, idx: int, distance: float | None):
        """
        Safely call user callback function for a specific sensor.
        
        :param idx: Index of the sensor
        :param distance: Measured distance or None if measurement failed
        """
        callback = self._user_callbacks[idx]
        if callback:
            try:
                micropython.schedule(lambda _: callback(self._trig_pins[idx], distance), 0)
            except RuntimeError:
                # Schedule queue full, call directly
                try:
                    callback(self._trig_pins[idx], distance)
                except Exception:
                    pass

    def _measure_single_sensor(self, idx: int, timeout_us: int = 30000) -> float | None:
        """
        Perform measurement on a single sensor.
        
        :param idx: Index of the sensor to measure
        :param timeout_us: Timeout for echo pulse in microseconds (default: 30000
        :return: Measured distance in cm or None if measurement failed
        """
        if self._nonblocking[idx]:
            # Skip sensors in non-blocking mode during manual read
            return None
        
        # Ensure trigger is LOW
        self._trig[idx] = 0
        utime.sleep_us(2)
        
        # Send trigger pulse
        self._trigger(idx)
        
        # Measure echo pulse duration
        try:
            duration_us = machine.time_pulse_us(self._echo[idx]._Din__din[0], 1, timeout_us)
        except Exception:
            return None
        
        # Check for timeout
        if duration_us < 0:
            return None
        
        # Convert time to distance
        speed_factor = self._cm_per_us(self._temp_c[idx])
        raw_distance = duration_us * speed_factor
        
        # Basic range validation
        if not (2.0 <= raw_distance <= 400.0):
            return None
        
        # Apply Kalman filter and return result
        filtered_distance = self._kalman1d(idx, raw_distance)
        return max(2.0, min(filtered_distance, 400.0))

    def _read_single(self, idx: int) -> float | None:
        """
        Read distance from a single sensor.
        
        :param idx: Index of the sensor to read
        :return: Measured distance in cm or None if measurement failed
        """
        return self._measure_single_sensor(idx)

    def _read_multiple(self, indices: list[int]) -> list[float | None]:
        """
        Read distances from multiple sensors.
        
        :param indices: List of sensor indices to read
        :return: List of measured distances in cm or None for each sensor
        """
        return [self._measure_single_sensor(idx) for idx in indices]

    def _timer_callback(self, timer):
        """
        Timer callback for non-blocking sensor measurements.
        
        :param timer: Timer instance that triggered the callback
        This method checks each sensor that is in non-blocking mode and performs measurements.
        """
        current_time = utime.ticks_ms()

        for i in range(len(self)):
            if not self._nonblocking[i] or not self._measurement_enabled:
                continue
            
            # Start new measurement if not active
            if not self._measurement_active[i]:
                try:
                    self._trigger(i)
                    self._measurement_start_time[i] = current_time
                    self._measurement_active[i] = True
                except Exception:
                    self._safe_call_callback(i, None)
                continue
            
            # Check if enough time has passed for measurement
            elapsed_ms = utime.ticks_diff(current_time, self._measurement_start_time[i])
            if elapsed_ms < 5:  # Wait at least 5ms after trigger
                continue
            
            # Try to read measurement
            try:
                duration_us = machine.time_pulse_us(self._echo[i]._Din__din[0], 1, 1000)  # Short timeout
                
                if duration_us >= 0:  # Valid measurement
                    speed_factor = self._cm_per_us(self._temp_c[i])
                    raw_distance = duration_us * speed_factor
                    
                    if 2.0 <= raw_distance <= 400.0:
                        filtered_distance = self._kalman1d(i, raw_distance)
                        distance = max(2.0, min(filtered_distance, 400.0))
                        self._safe_call_callback(i, distance)
                    else:
                        self._safe_call_callback(i, None)
                    
                    self._measurement_active[i] = False
                    
                elif elapsed_ms > 50:  # Timeout after 50ms
                    self._measurement_active[i] = False
                    self._safe_call_callback(i, None)
                    
            except Exception:
                if elapsed_ms > 50:  # Timeout
                    self._measurement_active[i] = False
                    self._safe_call_callback(i, None)

    def _start_timer(self):
        """
        Start the timer for non-blocking measurements.
        """
        if not self._timer_active:
            self._timer.init(
                period=self._period_ms,
                mode=machine.Timer.PERIODIC,
                callback=self._timer_callback
            )
            self._timer_active = True

    def _stop_timer(self):
        """
        Stop the timer for non-blocking measurements.
        """
        if self._timer_active:
            self._timer.deinit()
            self._timer_active = False
        
        # Reset measurement states
        for i in range(len(self)):
            self._measurement_active[i] = False

    @property
    def period_ms(self) -> int:
        """
        Get or set the measurement period for non-blocking mode.
        
        :return: Measurement period in milliseconds"""
        return self._period_ms

    @period_ms.setter
    def period_ms(self, ms: int):
        """
        Set the measurement period for non-blocking mode.
        This must be at least 10ms to ensure reliable operation.
        
        :param ms: Measurement period in milliseconds
        """
        if ms < 10:
            raise ValueError("Period must be at least 10ms")
        self._period_ms = int(ms)
        
        # Restart timer if active
        if self._timer_active:
            self._stop_timer()
            if self._measurement_enabled:
                self._start_timer()

    @property
    def measurement(self) -> bool:
        """
        Get or set the measurement state for non-blocking mode.
        
        :return: True if non-blocking measurements are enabled, False otherwise
        """
        return self._measurement_enabled

    @measurement.setter
    def measurement(self, enable: bool):
        """
        Enable or disable non-blocking measurements.
        
        :param enable: True to enable non-blocking measurements, False to disable
        """
        enable = bool(enable)

        if enable and not self._measurement_enabled:
            # Start measurements for sensors with callbacks
            nonblocking_sensors = [i for i in range(len(self)) 
                                 if self._nonblocking[i] and self._user_callbacks[i] is not None]
            
            if nonblocking_sensors:
                self._measurement_enabled = True
                self._start_timer()
            
        elif not enable and self._measurement_enabled:
            # Stop measurements
            self._measurement_enabled = False
            self._stop_timer()

    @property
    def filter_states(self) -> list[dict]:
        """
        Get the current Kalman filter states for all sensors.
        
        :return: List of dictionaries containing filter states for each sensor
        """
        return [
            {
                'position': self._x[i],
                'velocity': self._v[i],
                'covariance': [row[:] for row in self._P[i]],
                'measurement_noise': self._R[i],
                'process_noise': self._Q[i]
            }
            for i in range(len(self))
        ]

    class _SR04View:
        """A view class for controlling individual sensors or groups of sensors."""

        def __init__(self, parent: "SR04", indices: list[int]):
            """Initialize sensor view with parent reference and sensor indices."""
            self._parent = parent
            self._indices = indices

        def __getitem__(self, idx: int|slice) -> "SR04._SR04View":
            """Get a sub-view of this view."""
            if isinstance(idx, slice):
                selected_indices = [self._indices[i] for i in range(*idx.indices(len(self._indices)))]
                return SR04._SR04View(self._parent, selected_indices)
            else:
                return SR04._SR04View(self._parent, [self._indices[idx]])

        def __len__(self) -> int:
            """Get the number of sensors in this view."""
            return len(self._indices)

        def __iter__(self):
            """Iterate over measurement values from sensors in this view."""
            for idx in self._indices:
                yield self._parent._read_single(idx)

        def __repr__(self) -> str:
            """Return measurement values when printed directly."""
            values = self._get_values()
            return str(values[0] if len(values) == 1 else values)

        def _get_values(self) -> list[float|None]:
            """Internal method to get measurement values."""
            return [self._parent._read_single(idx) for idx in self._indices]

        def reset_filter(self):
            """Reset Kalman filters for sensors in this view."""
            for i in self._indices:
                self._parent._x[i] = 0.0
                self._parent._v[i] = 0.0
                self._parent._P[i] = [[1.0, 0.0], [0.0, 1.0]]

        @property
        def nonblocking(self) -> list[bool]:
            """Get or set non-blocking mode for sensors in this view."""
            return [self._parent._nonblocking[i] for i in self._indices]

        @nonblocking.setter
        def nonblocking(self, flag: bool):
            """Set non-blocking mode for sensors in this view."""
            flag = bool(flag)
            for i in self._indices:
                self._parent._nonblocking[i] = flag

        @property
        def temperature(self) -> list[float]:
            """Get or set temperatures for sensors in this view."""
            return [self._parent._temp_c[i] for i in self._indices]

        @temperature.setter
        def temperature(self, temp_c: float):
            """Set temperature for sensors in this view."""
            if not (-40.0 <= temp_c <= 85.0):
                raise ValueError("Temperature must be between -40°C and +85°C")
            temp_c = float(temp_c)
            for i in self._indices:
                self._parent._temp_c[i] = temp_c

        @property
        def filter(self) -> list[dict]:
            """Get or set Kalman filter parameters for sensors in this view."""
            return [{'R': self._parent._R[i], 'Q': self._parent._Q[i]} 
                   for i in self._indices]

        @filter.setter
        def filter(self, params: dict):
            """Set Kalman filter parameters for sensors in this view."""
            if not isinstance(params, dict):
                raise TypeError("Filter parameters must be a dictionary")
            
            for i in self._indices:
                if 'R' in params:
                    R = float(params['R'])
                    if R <= 0:
                        raise ValueError("R must be positive")
                    self._parent._R[i] = R
                
                if 'Q' in params:
                    Q = float(params['Q'])
                    if Q <= 0:
                        raise ValueError("Q must be positive")
                    self._parent._Q[i] = Q

        @property
        def callback(self) -> list[callable]:
            """Get or set callback functions for sensors in this view."""
            return [self._parent._user_callbacks[i] for i in self._indices]

        @callback.setter
        def callback(self, fn: callable):
            """Set callback function for sensors in this view."""
            for i in self._indices:
                self._parent._user_callbacks[i] = fn

        @property
        def filter_states(self) -> list[dict]:
            """Get filter states for sensors in this view."""
            all_states = self._parent.filter_states
            return [all_states[i] for i in self._indices]


@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    autopull=True,
    pull_thresh=24
)
def __ws2812_pio():
    T1 = 2
    T2 = 5
    T3 = 3
    label("bitloop")
    out(x, 1)           .side(0) [T3 - 1]
    jmp(not_x, "do0")   .side(1) [T1 - 1]
    jmp("bitloop")      .side(1) [T2 - 1]
    label("do0")
    nop()               .side(0) [T2 - 1]

class WS2812Matrix:
    def __init__(self, pin_sm_pairs:list[tuple[int,int]], *, panel_w:int=16, panel_h:int=16, grid_w:int=1,  grid_h:int=1, zigzag:bool=False, origin:str='top_left', brightness:float=0.25):
        """
        WS2812 Matrix controller using PIO for multiple panels.
        
        :param pin_sm_pairs: list of (pin_number, state_machine_id) tuples
        :param panel_w: width of each panel in pixels
        :param panel_h: height of each panel in pixels
        :param grid_w: number of panels in the grid width
        :param grid_h: number of panels in the grid height
        :param zigzag: if True, odd rows are reversed (zigzag wiring)
        :param origin: one of 'top_left', 'top_right', 'bottom_left', 'bottom_right'
        :param brightness: brightness level from 0.0 to 1.0
        """
        if origin not in ('top_left','top_right','bottom_left','bottom_right'):
            raise ValueError("origin must be top_left/top_right/bottom_left/bottom_right")
        
        mapping = pin_sm_pairs
        
        self.__panel_w  = panel_w
        self.__panel_h  = panel_h
        self.__grid_w   = grid_w
  
        self.__display_w   = panel_w * grid_w
        self.__display_h   = panel_h * grid_h

        self.__zigzag   = zigzag
        self.__origin   = origin
        self.brightness  = brightness

        self.__sms = [] 
        self.__bufs = []
        self.__panels_per_sm = math.ceil((grid_w * grid_h) / len(mapping))
        self.__pixels_per_panel = panel_w * panel_h

        for pin_no, sm_id in mapping:
            pin = machine.Pin(pin_no, machine.Pin.OUT, machine.Pin.PULL_DOWN)
            sm  = rp2.StateMachine(sm_id, __ws2812_pio, freq=8_000_000, sideset_base=pin)
            sm.active(1)
            self.__sms.append(sm)
            buf_len = self.__pixels_per_panel * self.__panels_per_sm
            self.__bufs.append(array.array('I', [0]*buf_len))
        
    def __coord_to_index(self, x:int, y:int):
        """
        Convert pixel coordinates (x, y) to the corresponding state machine and buffer index.
        
        :param x: x-coordinate (horizontal position)
        :param y: y-coordinate (vertical position)
        :return: (state_machine_index, buffer_index)
        """
        if not (0 <= x < self.__display_w and 0 <= y < self.__display_h):
            raise IndexError("pixel out of range")

        # calculate panel ID and local coordinates within the panel
        panel_col = x // self.__panel_w
        panel_row = y // self.__panel_h
        panel_id  = panel_row * self.__grid_w + panel_col

        # panel internal local coordinates
        lx = x % self.__panel_w
        ly = y % self.__panel_h

        # convert to panel-local coordinates
        if self.__origin.startswith('bottom'):
            ly = self.__panel_h - 1 - ly
        if self.__origin.endswith('right'):
            lx = self.__panel_w - 1 - lx
        
        # zigzag adjustment
        if self.__zigzag and (ly % 2):  # odd rows are reversed if zigzag is enabled
            lx = self.__panel_w - 1 - lx

        # SM / buffer index
        sm_idx   = panel_id // self.__panels_per_sm
        local_id = panel_id %  self.__panels_per_sm
        buf_idx  = local_id * self.__pixels_per_panel + ly * self.__panel_w + lx
        return sm_idx, buf_idx

    def deinit(self):
        """
        Deinitialize the WS2812 matrix controller.
        This method clears the buffers, stops the state machines, and resets the pins.
        """
        self.clear()
        utime.sleep_us(150)
        
        for sm in self.__sms:
            sm.active(0)
        for sm in self.__sms:
            sm.exec("set(pindirs, 1)")
            sm.exec("set(pins, 0)")

    @property
    def display_w(self) -> int:
        """
        Get the width of the display in pixels.
        
        :return: Width of the display in pixels
        """
        return self.__display_w

    @property
    def display_h(self) -> int:
        """
        Get the height of the display in pixels.
        
        :return: Height of the display in pixels
        """
        return self.__display_h

    @property
    def brightness(self) -> float:
        """
        Get the current brightness level of the matrix.
        The brightness level is a float value between 0.0 (off) and 1.0 (full brightness).
        
        :return: Brightness level (float)
        """
        return self.__bright

    @brightness.setter
    def brightness(self, value:float):
        """
        Set the brightness level of the matrix.
        The brightness level should be a float value between 0.0 (off) and 1.0 (full brightness).
        
        :param value: Brightness level (float)
        :raises ValueError: If the brightness value is not between 0.0 and 1.0.
        """
        self.__bright = max(0.0, min(value,1.0))
        b = self.__bright
        self.__btab = bytes(int(i * b + 0.5) for i in range(256))

    def __setitem__(self, pos:tuple[int,int], color:tuple[int,int,int]):
        """
        Set the color of a pixel at the specified position.
        The color should be a tuple of three integers representing the RGB values (0-255).
        
        :param pos: Tuple of (x, y) coordinates of the pixel
        :param color: Tuple of (R, G, B) color values
        :raises IndexError: If the pixel coordinates are out of range.
        """
        x,y = pos
        r,g,b = color
        sm_idx, buf_idx = self.__coord_to_index(x,y)
        self.__bufs[sm_idx][buf_idx] = (g & 0xFF)<<16 | (r & 0xFF)<<8 | (b & 0xFF)

    def __getitem__(self, pos) -> tuple[int,int,int]:
        """
        Get the color of a pixel at the specified position.
        The color is returned as a tuple of three integers representing the RGB values (0-255).
        
        :param pos: Tuple of (x, y) coordinates of the pixel
        :return: Tuple of (R, G, B) color values
        :raises IndexError: If the pixel coordinates are out of range.
        """
        x,y = pos
        sm_idx, buf_idx = self.__coord_to_index(x,y)
        v = self.__bufs[sm_idx][buf_idx]
        return ((v>>8)&0xFF, (v>>16)&0xFF, v&0xFF)

    def fill(self, color:tuple[int,int,int]):
        """
        Fill the entire display with the specified color.
        The color should be a tuple of three integers representing the RGB values (0-255).
        
        :param color: Tuple of (R, G, B) color values
        :raises ValueError: If the color values are not in the range 0-255.
        """
        grb = ((color[1]&0xFF)<<16) | ((color[0]&0xFF)<<8) | (color[2]&0xFF)
        for buf in self.__bufs:
            for i in range(len(buf)):
                buf[i] = grb
        self.update()

    def clear(self):
        """
        Clear the display by filling it with black (0, 0, 0).
        This method sets all pixels to black and updates the display.
        """
        self.fill((0,0,0))
        self.update()
        
    def update(self):
        """
        Update the display by sending the pixel data to the state machines.
        This method processes the pixel data in the buffers and sends it to the WS2812 panels.
        """
        btab = self.__btab
        for sm, src in zip(self.__sms, self.__bufs):
            tmp = array.array('I', [0]*len(src))
            for i, v in enumerate(src):
                g = btab[v>>16 & 0xFF]
                r = btab[v>>8  & 0xFF]
                b = btab[v     & 0xFF]
                tmp[i] = g<<16 | r<<8 | b
            sm.put(tmp, 8)

    def draw_line(self, x0:int, y0:int, x1:int, y1:int, color:tuple[int,int,int]):
        """
        Draw a line on the display from (x0, y0) to (x1, y1) with the specified color.
        
        :param x0: Starting x-coordinate of the line
        :param y0: Starting y-coordinate of the line
        :param x1: Ending x-coordinate of the line
        :param y1: Ending y-coordinate of the line
        :param color: Tuple of (R, G, B) color values
        """
        dx = abs(x1-x0); sx = 1 if x0<x1 else -1
        dy = -abs(y1-y0); sy = 1 if y0<y1 else -1
        err = dx + dy
        while True:
            self[x0,y0] = color
            if x0==x1 and y0==y1:
                break
            e2 = err<<1
            if e2 >= dy: 
                err += dy
                x0 += sx
            if e2 <= dx: 
                err += dx 
                y0 += sy

    def draw_rect(self, x:int, y:int, w:int, h:int, color:tuple[int,int,int]):
        """
        Draw a rectangle on the display with the specified position, width, height, and color.
        
        :param x: x-coordinate of the top-left corner of the rectangle
        :param y: y-coordinate of the top-left corner of the rectangle
        :param w: Width of the rectangle
        :param h: Height of the rectangle
        :param color: Tuple of (R, G, B) color values
        """
        self.draw_line(x,   y,   x+w-1, y,     color)
        self.draw_line(x,   y,   x,     y+h-1, color)
        self.draw_line(x+w-1, y, x+w-1, y+h-1, color)
        self.draw_line(x, y+h-1, x+w-1, y+h-1, color)

    def draw_circle(self, cx:int, cy:int, r:int, color:tuple[int,int,int]):
        """
        Draw a circle on the display with the specified center, radius, and color.
        
        :param cx: x-coordinate of the center of the circle
        :param cy: y-coordinate of the center of the circle
        :param r: Radius of the circle
        :param color: Tuple of (R, G, B) color values
        """
        x, y, err = r, 0, 0
        while x >= y:
            pts = [(cx+x,cy+y),(cx+y,cy+x),(cx-x,cy+y),(cx-y,cy+x),
                   (cx-x,cy-y),(cx-y,cy-x),(cx+x,cy-y),(cx+y,cy-x)]
            for px,py in pts:
                if 0 <= px < self.__display_w and 0 <= py < self.__display_h:
                    self[px,py] >= color
            y += 1
            if err <= 0:
                err += (y<<1) + 1
            if err > 0:
                x -= 1
                err -= (x<<1) + 1

    def blit(self, data, dst_x:int, dst_y:int, size_x:int, size_y:int, fg:tuple[int, int, int]=(255,255,255), bg:tuple[int, int, int]|None=None):
        """
        Blit a bitmap image onto the display at the specified position.
        The bitmap data can be a 2D list or a flat array of bytes.
        Each pixel is represented by a single byte (0 for black, 1 for white).
        
        :param data: Bitmap data as a 2D list or flat array of bytes
        :param dst_x: x-coordinate of the top-left corner where the bitmap will be drawn
        :param dst_y: y-coordinate of the top-left corner where the bitmap will be drawn
        :param size_x: Width of the bitmap in pixels
        :param size_y: Height of the bitmap in pixels
        :param fg: Foreground color as a tuple of (R, G, B) values (default is white)
        :param bg: Background color as a tuple of (R, G, B) values (default is None, which means no background)
        :raises ValueError: If the data is not in the expected format.
        """
        get = None
        if isinstance(data,(bytes,bytearray,memoryview)):
            def get(ix,iy):
                return data[iy*size_x+ix]
        else:
            get = lambda ix,iy: data[iy][ix]

        for iy in range(size_y):
            py = dst_y+iy
            if py<0 or py>=self.__display_h: continue
            for ix in range(size_x):
                px = dst_x+ix
                if px<0 or px>=self.__display_w: continue
                bit = get(ix,iy)
                if bit:
                    self[px,py] = fg
                elif bg is not None:
                    self[px,py] = bg


class tLed:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    WHITE = (255, 255, 255)
    
    def __init__(self, brightness:float=1.0):
        """
        Basic WS2812 control class built into TiCLE.
        This class provides methods to turn on the LED with a specified color,
        turn it off, and define some common colors.
        
        :param brightness: Brightness level from 0.0 (off) to 1.0 (full brightness).
        """

        self.__led = WS2812Matrix([(9,11)], 1, 1, 1, 1, brightness=brightness)

    def on(self, color:tuple[int,int,int]=RED):
        """
        Turn on the LED with the specified color.

        :param color: Tuple of (R, G, B) color values (default is red).
        """
        self.__led.fill(color)
        self.__led.update()
    
    def off(self):
        """
        Turn off the LED by filling it with black (0, 0, 0).
        """
        self.__led.clear()
        
    @property
    def brightness(self) -> float:
        """
        Get the current brightness level of the matrix.
        The brightness level is a float value between 0.0 (off) and 1.0 (full brightness).
        
        :return: Brightness level (float)
        """
        return self.__led.brightness

    @brightness.setter
    def brightness(self, value:float):
        """
        Set the brightness level of the matrix.
        The brightness level should be a float value between 0.0 (off) and 1.0 (full brightness).
        
        :param value: Brightness level (float)
        :raises ValueError: If the brightness value is not between 0.0 and 1.0.
        """
        if not (0.0 <= value <= 1.0):
            raise ValueError("Brightness must be between 0.0 and 1.0.")
        self.__led.brightness = value


class VL53L0X:
    """
    A class to interface with the VL53L0X time-of-flight distance sensor.
    This class provides methods to read distances, configure the sensor, and manage continuous measurements.
    It uses I2C communication to interact with the sensor.
    The sensor can measure distances from 30 mm to 1200 mm with a resolution of 1 mm.
    It supports both single-shot and continuous measurement modes.
    """
    __SYSRANGE_START = 0x00
    __SYS_SEQUENCE_CONFIG = 0x01
    __SYS_INTERRUPT_CONFIG_GPIO = 0x0A
    __GPIO_HV_MUX_HIGH = 0x84
    __SYS_INTERRUPT_CLEAR = 0x0B
    __REG_RESULT_INT_STATUS = 0x13
    __REG_RESULT_RANGE = 0x14
    __REG_MSRC_CONFIG = 0x60
    __REG_FINAL_RANGE_VCSEL = 0x70
    __REG_SPAD_ENABLES = 0xB0
    __REG_REF_START_SELECT = 0xB6
    __REG_DYNAMIC_SPAD_COUNT = 0x4E
    __REG_DYNAMIC_SPAD_OFFSET = 0x4F

    def __init__(self, scl: int, sda: int, addr: int = 0x29):
        """
        Initialize the VL53L0X sensor with the specified I2C pins and address.
        
        :param scl: GPIO pin number for the SCL line.
        :param sda: GPIO pin number for the SDA line.
        :param addr: I2C address of the sensor (default is 0x29).
        """
        self.__bus = I2c(scl=scl, sda=sda, addr=addr)
        self.__measurement_active = False
        self.__initialize_sensor()
        self.__timing_budget_us = 33000
        self.__measurement_timing_budget = 33000  # triggers property setter to configure registers

    def read_distance(self) -> int:
        """
        Read the distance measurement from the sensor.
        This method triggers a measurement if one is not already active,
        waits for the measurement to complete, and then fetches the distance.
        
        :return: Distance in millimeters, or None if the measurement is not ready.
        """
        if not self.__measurement_active:
            self.__trigger_measurement()
        while not self.__is_measurement_ready():
            utime.sleep_ms(1)
        return self.__fetch_distance()

    def start_continuous(self, period_ms: int = 0) -> None:
        """
        Start continuous measurements with the specified period in milliseconds.
        If period_ms is 0, continuous measurements will run at the default timing budget.

        :param period_ms: Measurement period in milliseconds (default is 0, which uses the timing budget).
        :raises ValueError: If period_ms is less than the minimum required period.
        """
        min_period = self.__timing_budget_us // 1000 + 5
        if period_ms and period_ms < min_period:
            raise ValueError(f"period_ms must be ≥{min_period}")
        self.__bus.write_u8(0x80, 1)
        self.__bus.write_u8(0xFF, 1)
        self.__bus.write_u8(0, 0)
        if period_ms:
            self.__bus.write_u8(0x91, self.__stop_reg)
            self.__bus.write_u8(0, 1)
            self.__bus.write_u8(0x04, period_ms * 1000)
        else:
            self.__bus.write_u8(0, 0)
        self.__bus.write_u8(0xFF, 0)
        self.__bus.write_u8(0x80, 0)
        self.__bus.write_u8(self.__SYSRANGE_START, 0x02)

    def stop_continuous(self) -> None:
        """
        Stop continuous measurements and reset the sensor to single-shot mode.
        This method clears the interrupt and stops the measurement.
        """
        self.__bus.write_u8(self.__SYSRANGE_START, 0x01)
        self.__bus.write_u8(self.__SYS_INTERRUPT_CLEAR, 1)

    def read_continuous(self) -> int | None:
        """
        Read the distance measurement in continuous mode.
        This method checks if a measurement is ready, and if so, fetches the distance.
        
        :return: Distance in millimeters, or None if no measurement is ready.
        """
        if (self.__bus.read_u8(self.__REG_RESULT_INT_STATUS) & 0x07) == 0:
            return None
        result = self.__bus.read_u16(self.__REG_RESULT_RANGE + 10, little_endian=False)
        self.__bus.write_u8(self.__SYS_INTERRUPT_CLEAR, 1)
        return result

    def configure_long_range(self) -> None:
        """
        Configure the sensor for long-range measurements.
        This method sets the minimum signal rate and adjusts the final range VCSEL period.
        """
        self.__min_signal_rate = 0.05
        self.__bus.write_u8(self.__REG_FINAL_RANGE_VCSEL, (16 >> 1) - 1)
        self.set_timing_budget(40000)

    def configure_high_speed(self) -> None:
        """
        Configure the sensor for high-speed measurements.
        This method sets the minimum signal rate and adjusts the final range VCSEL period.
        """
        self.__min_signal_rate = 0.25
        self.set_timing_budget(20000)

    def set_timing_budget(self, budget_us: int) -> None:
        """
        Set the measurement timing budget in microseconds.
        This method updates the timing budget and configures the sensor registers accordingly.

        :param budget_us: Timing budget in microseconds (must be between 20000 and 330000).
        :raises ValueError: If budget_us is outside the valid range.
        """
        # Single assignment triggers register update
        self.__measurement_timing_budget = budget_us
        self.__timing_budget_us = budget_us

    def __decode_timeout_mclks(self, val: int) -> float:
        """
        Decode the timeout value from the sensor registers into microseconds.
        
        :param val: Encoded timeout value from the sensor registers.
        :return: Timeout in microseconds.
        """
        return float(val & 0xFF) * (2 ** ((val >> 8) & 0xFF)) + 1

    def __encode_timeout_mclks(self, mclks: int) -> int:
        """
        Encode the timeout value in microseconds into the format used by the sensor registers.
        
        :param mclks: Timeout in microseconds.
        :return: Encoded timeout value for the sensor registers.
        """
        m = mclks - 1
        e = 0
        while m > 0xFF:
            m >>= 1
            e += 1
        return ((e << 8) | (m & 0xFF)) & 0xFFFF

    def __mclks_to_microseconds(self, mclks: int, vcsel_period: int) -> int:
        """
        Convert macro clock cycles to microseconds.
        This method calculates the time in microseconds based on the number of macro clock cycles
        and the VCSEL period.
        
        :param mclks: Number of macro clock cycles.
        :param vcsel_period: VCSEL period in microseconds.
        :return: Time in microseconds.
        """
        macro_ns = ((2304 * vcsel_period * 1655) + 500) // 1000
        return ((mclks * macro_ns) + (macro_ns // 2)) // 1000

    def __microseconds_to_mclks(self, us: int, vcsel_period: int) -> int:
        """
        Convert microseconds to macro clock cycles.
        This method calculates the number of macro clock cycles based on the time in microseconds
        and the VCSEL period.

        :param us: Time in microseconds.
        :param vcsel_period: VCSEL period in microseconds.
        :return: Number of macro clock cycles.
        """
        macro_ns = ((2304 * vcsel_period * 1655) + 500) // 1000
        return ((us * 1000) + (macro_ns // 2)) // macro_ns

    def __trigger_measurement(self) -> None:
        """
        Trigger a single measurement by writing to the SYSRANGE_START register.
        This method checks if a measurement is already active, and if not, it clears the interrupt
        and starts a new measurement.
        """
        if self.__measurement_active:
            return
        self.__bus.write_u8(self.__SYS_INTERRUPT_CLEAR, 0x01)
        self.__bus.write_u8(self.__SYSRANGE_START, 0x01)
        self.__measurement_active = True

    def __is_measurement_ready(self) -> bool:
        """
        Check if a measurement is ready by reading the interrupt status register.
        This method returns True if a measurement is ready, otherwise it returns False.
        
        :return: True if measurement is ready, False otherwise.
        """
        if not self.__measurement_active:
            return False
        return (self.__bus.read_u8(self.__REG_RESULT_INT_STATUS) & 0x07) != 0

    def __fetch_distance(self) -> int:
        """
        Fetch the distance measurement from the sensor registers.
        This method reads the distance value from the RESULT_RANGE register,
        clears the interrupt, and stops the measurement.
        
        :return: Distance in millimeters.
        """
        distance = self.__bus.read_u16(self.__REG_RESULT_RANGE + 10, little_endian=False)
        self.__bus.write_u8(self.__SYS_INTERRUPT_CLEAR, 0x01)
        self.__bus.write_u8(self.__SYSRANGE_START, 0x00)
        self.__measurement_active = False
        return distance

    def __write_register_sequence(self, seq:tuple[tuple[int, int], ...]) -> None:
        """
        Write a sequence of register-value pairs to the sensor.
        This method takes a sequence of tuples, where each tuple contains a register address and a value,
        and writes them to the sensor's registers using I2C communication.

        :param seq: Sequence of tuples (register, value) to write to the sensor.
        """
        for reg, val in seq:
            self.__bus.write_u8(reg, val)

    def __initialize_sensor(self) -> None:
        """
        Initialize the VL53L0X sensor by performing a series of register writes
        """
        id_bytes = self.__bus.readfrom_mem(0xC0, 3)
        if id_bytes != b'\xEE\xAA\x10':
            raise RuntimeError("Sensor ID mismatch", id_bytes)
        self.__write_register_sequence(((0x88,0x00),(0x80,0x01),(0xFF,0x01),(0x00,0x00)))
        self.__stop_reg = self.__bus.read_u8(0x91)
        self.__write_register_sequence(((0x00,0x01),(0xFF,0x00),(0x80,0x00)))
        cfg = self.__bus.read_u8(self.__REG_MSRC_CONFIG)
        self.__bus.write_u8(self.__REG_MSRC_CONFIG, cfg | 0x12)
        self.__min_signal_rate = 0.25
        self.__bus.write_u8(self.__SYS_SEQUENCE_CONFIG, 0xFF)
        spad_count, spad_type = self.__retrieve_spad_info()
        spad_map = bytearray(7)
        self.__bus.readfrom_mem_into(self.__REG_SPAD_ENABLES, spad_map)
        self.__write_register_sequence(((0xFF,0x01),(self.__REG_DYNAMIC_SPAD_OFFSET,0x00),(self.__REG_DYNAMIC_SPAD_COUNT,0x2C),(0xFF,0x00),(self.__REG_REF_START_SELECT,0xB4)))
        first = 12 if spad_type else 0
        enabled = 0
        for i in range(48):
            idx = 1 + (i // 8)
            if i < first or enabled == spad_count:
                spad_map[idx] &= ~(1 << (i % 8))
            elif (spad_map[idx] >> (i % 8)) & 1:
                enabled += 1
        self.__bus.writeto_mem(self.__REG_SPAD_ENABLES, spad_map)
        seq = (
            (0xFF,0x01),(0x00,0x00),(0xFF,0x00),(0x09,0x00),(0x10,0x00),(0x11,0x00),(0x24,0x01),(0x25,0xFF),
            (0x75,0x00),(0xFF,0x01),(0x4E,0x2C),(0x48,0x00),(0x30,0x20),(0xFF,0x00),(0x30,0x09),(0x54,0x00),
            (0x31,0x04),(0x32,0x03),(0x40,0x83),(0x46,0x25),(0x60,0x00),(0x27,0x00),(0x50,0x06),(0x51,0x00),
            (0x52,0x96),(0x56,0x08),(0x57,0x30),(0x61,0x00),(0x62,0x00),(0x64,0x00),(0x65,0x00),(0x66,0xA0),
            (0xFF,0x01),(0x22,0x32),(0x47,0x14),(0x49,0xFF),(0x4A,0x00),(0xFF,0x00),(0x7A,0x0A),(0x7B,0x00),
            (0x78,0x21),(0xFF,0x01),(0x23,0x34),(0x42,0x00),(0x44,0xFF),(0x45,0x26),(0x46,0x05),(0x40,0x40),
            (0x0E,0x06),(0x20,0x1A),(0x43,0x40),(0xFF,0x00),(0x34,0x03),(0x35,0x44),(0xFF,0x01),(0x31,0x04),
            (0x4B,0x09),(0x4C,0x05),(0x4D,0x04),(0xFF,0x00),(0x44,0x00),(0x45,0x20),(0x47,0x08),(0x48,0x28),
            (0x67,0x00),(0x70,0x04),(0x71,0x01),(0x72,0xFE),(0x76,0x00),(0x77,0x00),(0xFF,0x01),(0x0D,0x01),
            (0xFF,0x00),(0x80,0x01),(0x01,0xF8),(0xFF,0x01),(0x8E,0x01),(0x00,0x01),(0xFF,0x00),(0x80,0x00)
        )
        self.__write_register_sequence(seq)
        self.__bus.write_u8(self.__SYS_INTERRUPT_CONFIG_GPIO, 0x04)
        gpio = self.__bus.read_u8(self.__GPIO_HV_MUX_HIGH)
        self.__bus.write_u8(self.__GPIO_HV_MUX_HIGH, gpio & ~0x10)
        self.__bus.write_u8(self.__SYS_INTERRUPT_CLEAR, 0x01)
        self.__measurement_timing_budget = self.__calculate_timing_budget()
        self.__bus.write_u8(self.__SYS_SEQUENCE_CONFIG, 0xE8)
        self.__bus.write_u8(self.__SYS_SEQUENCE_CONFIG, 0x01)
        self.__single_ref_calibration(0x40)
        self.__bus.write_u8(self.__SYS_SEQUENCE_CONFIG, 0x02)
        self.__single_ref_calibration(0x00)
        self.__bus.write_u8(self.__SYS_SEQUENCE_CONFIG, 0xE8)


class VL53L0X_old:
    """
    This VL53L0X driver implements I²C-based communication with ST’s Time-of-Flight distance sensor, 
    providing a streamlined interface to initialize the module, 
    configure ranging modes (single-shot or continuous), 
    and retrieve distance measurements with up to 120 cm range and ±13° field of view. 
    """
    __SYSRANGE_START = 0x00
    __SYSTEM_SEQUENCE_CONFIG = 0x01
    __SYSTEM_INTERRUPT_CONFIG_GPIO = 0x0A
    __GPIO_HV_MUX_ACTIVE_HIGH = 0x84
    __SYSTEM_INTERRUPT_CLEAR = 0x0B
    __RESULT_INTERRUPT_STATUS = 0x13
    __RESULT_RANGE_STATUS = 0x14
    __MSRC_CONFIG_CONTROL = 0x60
    __FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT = 0x44
    __PRE_RANGE_CONFIG_VCSEL_PERIOD = 0x50
    __PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI = 0x51
    __FINAL_RANGE_CONFIG_VCSEL_PERIOD = 0x70
    __FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI = 0x71
    __MSRC_CONFIG_TIMEOUT_MACROP = 0x46
    __GLOBAL_CONFIG_SPAD_ENABLES_REF_0 = 0xB0
    __GLOBAL_CONFIG_REF_EN_START_SELECT = 0xB6
    __DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD = 0x4E
    __DYNAMIC_SPAD_REF_EN_START_OFFSET = 0x4F
    __VCSEL_PERIOD_PRE_RANGE = 0
    __VCSEL_PERIOD_FINAL_RANGE = 1


    def __init__(self, scl:int,  sda:int, addr:int=0x29):
        """
        Initialize the VL53L0X sensor.
        This method sets up the I2C communication with the sensor and performs initial configuration.

        :param scl: GPIO pin number for SCL (I2C clock)
        :param sda: GPIO pin number for SDA (I2C data)
        :param addr: I2C address of the sensor (default: 0x29)
        """
        self._i2c = I2c(scl=scl, sda=sda, addr=addr)
        
        self.__range_started = False
        self._init_sensor()
        self._timing_budget_us = 33000
        
    def read(self):
        """
        Read the distance measurement from the sensor.
        
        :return: Distance in mm (millimeters)
        """
        if not self.__range_started:
            self._start_range_request()

        while not self._reading_available():
            utime.sleep_ms(1)

        return self._get_range_value()

    def start_continuous(self, period_ms=0):
        """
        Start continuous ranging mode.
        This method configures the sensor to continuously measure distances at a specified period.
        
        :param period_ms: Measurement period in milliseconds (default: 0, which uses the timing budget)
        """
        min_period = self._timing_budget_us // 1000 + 5
        if period_ms and period_ms < min_period:
            raise ValueError("period_ms must be ≥%d" % min_period)

        self._i2c.write_u8(0x80,1); self._i2c.write_u8(0xFF,1); self._i2c.write_u8(0,0)
        if period_ms:
            self._i2c.write_u8(0x91, self._stop_variable)
            self._i2c.write_u8(0,1)
            self._i2c.write_u8(0x04, period_ms*1000)
        else:
            self._i2c.write_u8(0,0)
        self._i2c.write_u8(0xFF,0); self._i2c.write_u8(0x80,0)

        self._i2c.write_u8(self.__SYSRANGE_START, 0x02) 

    def stop_continuous(self):
        """
        Stop continuous ranging mode.
        """
        self._i2c.write_u8(self.__SYSRANGE_START, 0x01)
        self._i2c.write_u8(self.__SYSTEM_INTERRUPT_CLEAR, 1)

    def read_continuous(self):
        """
        Read the distance measurement in continuous mode.
        
        :return: Distance in mm (millimeters) or None if no measurement is available
        """
        if (self._i2c.read_u8(self.__RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            return None
        rng = self._i2c.read_u16(self.__RESULT_RANGE_STATUS + 10, little_endian=False)
        self._i2c.write_u8(self.__SYSTEM_INTERRUPT_CLEAR, 1)
        return rng

    def set_long_range(self):
        """
        Set the sensor to long range mode.
        """
        self._signal_rate_limit = 0.05        # MCPS under ↓
        self._i2c.write_u8(self.__FINAL_RANGE_CONFIG_VCSEL_PERIOD, (16 >> 1) - 1)  # VCSEL = 16 PCLK
        self.set_timing_budget(40000)

    def set_high_speed(self):
        """
        Set the sensor to high speed mode.
        """
        self._signal_rate_limit = 0.25
        self.set_timing_budget(20000)

    def set_timing_budget(self, budget_us):
        """
        Set the measurement timing budget.
        """
        self._measurement_timing_budget = budget_us
        self._timing_budget_us = budget_us
        
    # ST Library functions START
    def _decode_timeout(self, val):
        return float(val & 0xFF) * math.pow(2.0, ((val & 0xFF00) >> 8)) + 1

    def _encode_timeout(self, timeout_mclks):
        timeout_mclks = int(timeout_mclks) & 0xFFFF
        ls_byte = 0
        ms_byte = 0
        if timeout_mclks > 0:
            ls_byte = timeout_mclks - 1
            while ls_byte > 255:
                ls_byte >>= 1
                ms_byte += 1
            return ((ms_byte << 8) | (ls_byte & 0xFF)) & 0xFFFF
        return 0

    def _timeout_mclks_to_microseconds(self, timeout_period_mclks, vcsel_period_pclks):
        macro_period_ns = ((2304 * (vcsel_period_pclks) * 1655) + 500) // 1000
        return ((timeout_period_mclks * macro_period_ns) + (macro_period_ns // 2)) // 1000

    def _timeout_microseconds_to_mclks(self, timeout_period_us, vcsel_period_pclks):
        macro_period_ns = ((2304 * (vcsel_period_pclks) * 1655) + 500) // 1000
        return ((timeout_period_us * 1000) + (macro_period_ns // 2)) // macro_period_ns
    # ST Library functions END

    def _start_range_request(self):
        if self.__range_started == True: 
            return

        """old code
        for reg, val in ((0x80, 0x01), (0xFF, 0x01), (0x00, 0x00), (0x91, self._stop_variable), (0x00, 0x01), (0xFF, 0x00), (0x80, 0x00)):
            self._i2c.write_u8(reg, val)
        """
        self._i2c.write_u8(self.__SYSTEM_INTERRUPT_CLEAR, 0x01)
        self._i2c.write_u8(self.__SYSRANGE_START, 0x01)
        self.__range_started = True        

    def _reading_available(self):
        if self.__range_started == False: 
            return False
        
        return (self._i2c.read_u8(self.__RESULT_INTERRUPT_STATUS) & 0x07) != 0

    def _get_range_value(self):
        if not self.__range_started:
            return None

        rng = self._i2c.read_u16(self.__RESULT_RANGE_STATUS + 10, little_endian=False)
        self._i2c.write_u8(self.__SYSTEM_INTERRUPT_CLEAR, 0x01) 
        self._i2c.write_u8(self.__SYSRANGE_START, 0x00) 
        self.__range_started = False
        
        return rng
    
    def _set_register(self, config:tuple):
        """
        Configure the sensor with the given configuration.\r
\1 config: tuple containing register addresses and values
        """
        for reg, val in config:
            self._i2c.write_u8(reg, val)
    
    def _init_sensor(self):
        id_bytes = self._i2c.readfrom_mem(0xC0, 3)
        if id_bytes != b'\xEE\xAA\x10':
            raise RuntimeError("Failed to find expected ID register values. (C0,C1,C2):", id_bytes)
                
        self._set_register( ((0x88, 0x00), (0x80, 0x01), (0xFF, 0x01), (0x00, 0x00)) )

        self._stop_variable = self._i2c.read_u8(0x91)

        self._set_register( ((0x00, 0x01), (0xFF, 0x00), (0x80, 0x00)) )

        config_control = self._i2c.read_u8(self.__MSRC_CONFIG_CONTROL) | 0x12
        self._i2c.write_u8(self.__MSRC_CONFIG_CONTROL, config_control)

        self._signal_rate_limit = 0.25
        self._i2c.write_u8(self.__SYSTEM_SEQUENCE_CONFIG, 0xFF)
        spad_count, spad_is_aperture = self._get_spad_info()

        ref_spad_map = bytearray(7)
        self._i2c.readfrom_mem_into(self.__GLOBAL_CONFIG_SPAD_ENABLES_REF_0, ref_spad_map)

        self._set_register(
            ((0xFF, 0x01),
            (self.__DYNAMIC_SPAD_REF_EN_START_OFFSET, 0x00),
            (self.__DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD, 0x2C),
            (0xFF, 0x00),
            (self.__GLOBAL_CONFIG_REF_EN_START_SELECT, 0xB4))
        )

        first_spad_to_enable = 12 if spad_is_aperture else 0
        spads_enabled = 0
        
        for i in range(48):
            if i < first_spad_to_enable or spads_enabled == spad_count:
                ref_spad_map[1 + (i // 8)] &= ~(1 << (i % 8))
            elif (ref_spad_map[1 + (i // 8)] >> (i % 8)) & 0x1 > 0:
                spads_enabled += 1
        
        self._i2c.writeto_mem(self.__GLOBAL_CONFIG_SPAD_ENABLES_REF_0, ref_spad_map)
        
        self._set_register(
            ((0xFF, 0x01), (0x00, 0x00), (0xFF, 0x00), (0x09, 0x00), (0x10, 0x00), (0x11, 0x00), (0x24, 0x01), (0x25, 0xFF),
            (0x75, 0x00), (0xFF, 0x01), (0x4E, 0x2C), (0x48, 0x00), (0x30, 0x20), (0xFF, 0x00), (0x30, 0x09), (0x54, 0x00),
            (0x31, 0x04), (0x32, 0x03), (0x40, 0x83), (0x46, 0x25), (0x60, 0x00), (0x27, 0x00), (0x50, 0x06), (0x51, 0x00),
            (0x52, 0x96), (0x56, 0x08), (0x57, 0x30), (0x61, 0x00), (0x62, 0x00), (0x64, 0x00), (0x65, 0x00), (0x66, 0xA0),
            (0xFF, 0x01), (0x22, 0x32), (0x47, 0x14), (0x49, 0xFF), (0x4A, 0x00), (0xFF, 0x00), (0x7A, 0x0A), (0x7B, 0x00),
            (0x78, 0x21), (0xFF, 0x01), (0x23, 0x34), (0x42, 0x00), (0x44, 0xFF), (0x45, 0x26), (0x46, 0x05), (0x40, 0x40),
            (0x0E, 0x06), (0x20, 0x1A), (0x43, 0x40), (0xFF, 0x00), (0x34, 0x03), (0x35, 0x44), (0xFF, 0x01), (0x31, 0x04),
            (0x4B, 0x09), (0x4C, 0x05), (0x4D, 0x04), (0xFF, 0x00), (0x44, 0x00), (0x45, 0x20), (0x47, 0x08), (0x48, 0x28),
            (0x67, 0x00), (0x70, 0x04), (0x71, 0x01), (0x72, 0xFE), (0x76, 0x00), (0x77, 0x00), (0xFF, 0x01), (0x0D, 0x01),
            (0xFF, 0x00), (0x80, 0x01), (0x01, 0xF8), (0xFF, 0x01), (0x8E, 0x01), (0x00, 0x01), (0xFF, 0x00), (0x80, 0x00))
        )

        self._i2c.write_u8(self.__SYSTEM_INTERRUPT_CONFIG_GPIO, 0x04)
        gpio_hv_mux_active_high = self._i2c.read_u8(self.__GPIO_HV_MUX_ACTIVE_HIGH)
        self._i2c.write_u8(self.__GPIO_HV_MUX_ACTIVE_HIGH, gpio_hv_mux_active_high & ~0x10)
        self._i2c.write_u8(self.__SYSTEM_INTERRUPT_CLEAR, 0x01)
        self._measurement_timing_budget_us = self._measurement_timing_budget
        self._i2c.write_u8(self.__SYSTEM_SEQUENCE_CONFIG, 0xE8)
        self._measurement_timing_budget = self._measurement_timing_budget_us
        self._i2c.write_u8(self.__SYSTEM_SEQUENCE_CONFIG, 0x01)
        self._perform_single_ref_calibration(0x40)
        self._i2c.write_u8(self.__SYSTEM_SEQUENCE_CONFIG, 0x02)
        self._perform_single_ref_calibration(0x00)
        self._i2c.write_u8(self.__SYSTEM_SEQUENCE_CONFIG, 0xE8)
    
    def _get_spad_info(self):
        self._set_register( ((0x80, 0x01), (0xFF, 0x01), (0x00, 0x00), (0xFF, 0x06)) )
        self._i2c.write_u8(0x83, self._i2c.read_u8(0x83) | 0x04)
        self._set_register( ((0xFF, 0x07), (0x81, 0x01), (0x80, 0x01), (0x94, 0x6B), (0x83, 0x00)) )

        while self._i2c.read_u8(0x83) == 0x00:
            utime.sleep_ms(1)
            
        self._i2c.write_u8(0x83, 0x01)
        tmp = self._i2c.read_u8(0x92)
        count = tmp & 0x7F
        is_aperture = ((tmp >> 7) & 0x01) == 1
        
        self._set_register( ((0x81, 0x00), (0xFF, 0x06)) )        
        self._i2c.write_u8(0x83, self._i2c.read_u8(0x83) & ~0x04)
        self._set_register( ((0xFF, 0x01), (0x00, 0x01), (0xFF, 0x00), (0x80, 0x00)) )
        
        return (count, is_aperture)

    def _perform_single_ref_calibration(self, vhv_init_byte):
        self._i2c.write_u8(self.__SYSRANGE_START, 0x01 | vhv_init_byte & 0xFF)
        
        while (self._i2c.read_u8(self.__RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            utime.sleep_ms(1)
            
        self._i2c.write_u8(self.__SYSTEM_INTERRUPT_CLEAR, 0x01)
        self._i2c.write_u8(self.__SYSRANGE_START, 0x00)

    def _get_vcsel_pulse_period(self, vcsel_period_type):
        ret = 255
        
        if vcsel_period_type == self.__VCSEL_PERIOD_PRE_RANGE:
            val = self._i2c.read_u8(self.__PRE_RANGE_CONFIG_VCSEL_PERIOD)
            ret = (((val) + 1) & 0xFF) << 1
        elif vcsel_period_type == self.__VCSEL_PERIOD_FINAL_RANGE:
            val = self._i2c.read_u8(self.__FINAL_RANGE_CONFIG_VCSEL_PERIOD)
            ret = (((val) + 1) & 0xFF) << 1
        
        return ret

    def _get_sequence_step_enables(self):
        sequence_config = self._i2c.read_u8(self.__SYSTEM_SEQUENCE_CONFIG)
        tcc = (sequence_config >> 4) & 0x1 > 0
        dss = (sequence_config >> 3) & 0x1 > 0
        msrc = (sequence_config >> 2) & 0x1 > 0
        pre_range = (sequence_config >> 6) & 0x1 > 0
        final_range = (sequence_config >> 7) & 0x1 > 0
        
        return (tcc, dss, msrc, pre_range, final_range)

    def _get_sequence_step_timeouts(self, pre_range):
        pre_range_vcsel_period_pclks = self._get_vcsel_pulse_period(self.__VCSEL_PERIOD_PRE_RANGE)
        msrc_dss_tcc_mclks = (self._i2c.read_u8(self.__MSRC_CONFIG_TIMEOUT_MACROP) + 1) & 0xFF
        msrc_dss_tcc_us = self._timeout_mclks_to_microseconds(msrc_dss_tcc_mclks, pre_range_vcsel_period_pclks)
        pre_range_mclks = self._decode_timeout(self._i2c.read_u16(self.__PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI, little_endian=False))
        pre_range_us = self._timeout_mclks_to_microseconds(pre_range_mclks, pre_range_vcsel_period_pclks)
        final_range_vcsel_period_pclks = self._get_vcsel_pulse_period(self.__VCSEL_PERIOD_FINAL_RANGE)
        final_range_mclks = self._decode_timeout(self._i2c.read_u16(self.__FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI, little_endian=False))
        if pre_range:
            final_range_mclks -= pre_range_mclks
            
        final_range_us = self._timeout_mclks_to_microseconds(final_range_mclks, final_range_vcsel_period_pclks)
        
        return (msrc_dss_tcc_us, pre_range_us, final_range_us, final_range_vcsel_period_pclks, pre_range_mclks)

    @property
    def _signal_rate_limit(self):
        val = self._i2c.read_u16(self.__FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT, little_endian=False)

        return val / (1 << 7)

    @_signal_rate_limit.setter
    def _signal_rate_limit(self, val):
        assert 0.0 <= val <= 511.99

        val = int(val * (1 << 7))
        self._i2c.write_u16(self.__FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT, val)

    @property
    def _measurement_timing_budget(self):

        budget_us = 1910 + 960
        tcc, dss, msrc, pre_range, final_range = self._get_sequence_step_enables()
        step_timeouts = self._get_sequence_step_timeouts(pre_range)
        msrc_dss_tcc_us, pre_range_us, final_range_us, _, _ = step_timeouts
        
        if tcc:
            budget_us += msrc_dss_tcc_us + 590
        if dss:
            budget_us += 2 * (msrc_dss_tcc_us + 690)
        elif msrc:
            budget_us += msrc_dss_tcc_us + 660
        if pre_range:
            budget_us += pre_range_us + 660
        if final_range:
            budget_us += final_range_us + 550
        self._measurement_timing_budget_us = budget_us
        
        return budget_us

    @_measurement_timing_budget.setter
    def _measurement_timing_budget(self, budget_us):
        assert budget_us >= 20000
        
        used_budget_us = 1320 + 960
        tcc, dss, msrc, pre_range, final_range = self._get_sequence_step_enables()
        step_timeouts = self._get_sequence_step_timeouts(pre_range)
        msrc_dss_tcc_us, pre_range_us, _ = step_timeouts[:3]
        final_range_vcsel_period_pclks, pre_range_mclks = step_timeouts[3:]
        
        if tcc:
            used_budget_us += msrc_dss_tcc_us + 590
        if dss:
            used_budget_us += 2 * (msrc_dss_tcc_us + 690)
        elif msrc:
            used_budget_us += msrc_dss_tcc_us + 660
        if pre_range:
            used_budget_us += pre_range_us + 660
        if final_range:
            used_budget_us += 550

            if used_budget_us > budget_us:
                raise ValueError("Requested timeout too big.")
            
            final_range_timeout_us = budget_us - used_budget_us
            final_range_timeout_mclks = self._timeout_microseconds_to_mclks(final_range_timeout_us, final_range_vcsel_period_pclks)
            
            if pre_range:
                final_range_timeout_mclks += pre_range_mclks
            self._i2c.write_u16(self.__FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI, self._encode_timeout(final_range_timeout_mclks))
            self._measurement_timing_budget_us = budget_us


class BNO055:
    """
    A class to read data from the BNO055 9-DoF sensor.
    This class provides methods to read acceleration, gyroscope, magnetic field, Euler angles, quaternion, and temperature data.
    """
    ACCELERATION  = 0x08   # raw accel (include gravity)
    MAGNETIC      = 0x0E
    GYROSCOPE     = 0x14
    EULER         = 0x1A
    QUATERNION    = 0x20
    ACCEL_LINEAR  = 0x28   # linear accel (exclude gravity)
    ACCEL_GRAVITY = 0x2E
    TEMPERATURE   = 0x34

    __MODE_CONFIG  = 0x00
    __MODE_NDOF    = 0x0C
    __PWR_NORMAL   = 0x00

    __SCALE = {
        ACCELERATION : 1/100,           # m/s² (1 LSB = 0.01 m/s²)
        ACCEL_LINEAR : 1/100,
        ACCEL_GRAVITY: 1/100,
        MAGNETIC     : 1/16,            # µT
        GYROSCOPE    : 1/900,           # rad/s (0.0625 °/s)
        EULER        : 1/16,            # °
        QUATERNION   : 1/(1<<14),       # dimensionless
    }

    def __init__(self, scl:int, sda:int, addr:int=0x28, freq:int=400_000):
        """
        Initialize the BNO055 sensor.
        
        :param scl: SCL pin number (GPIO pin)
        :param sda: SDA pin number (GPIO pin)
        :param addr: I2C address of the BNO055 sensor (default is 0x28)
        :param freq: I2C frequency (default is 400kHz)
        """
        self._i2c  = I2c(scl=scl, sda=sda, addr=addr, freq=freq)

        w8 = self._i2c.write_u8

        w8(0x3F, 0x20)                 # SYS_TRIGGER – reset
        utime.sleep_ms(700)

        w8(0x3D, self.__MODE_CONFIG)    # OPR_MODE – CONFIG
        utime.sleep_ms(25)

        w8(0x3E, self.__PWR_NORMAL)     # PWR_MODE – Normal
        w8(0x07, 0x00)                 # PAGE_ID   – page 0

        w8(0x3F, 0x80)                 # use external crystal
        utime.sleep_ms(10)

        w8(0x3D, self.__MODE_NDOF)      # OPR_MODE – NDOF(9-DoF)
        utime.sleep_ms(20)

    def __read_vector(self, reg, count, conv):
        """
        Read a vector of integers from the specified register.
        
        :param reg: The register address to read from.
        :param count: The number of integers to read.
        :param conv: The conversion factor to apply to the read integers.
        :return: A tuple of integers, converted if `conv` is not None.
        """
        data = self._i2c.readfrom_mem(reg, count*2)
        ints = ustruct.unpack('<' + 'h'*count, data)
        if conv is None:
            return ints              # raw
        if count == 1:
            return ints[0] * conv
        return tuple(v * conv for v in ints)

    def temperature(self) -> int:
        """
        Read the temperature from the BNO055 sensor.
        
        :return: The temperature in degrees Celsius.
        """
        t = self._i2c.read_u8(self.TEMPERATURE)
        return t - 256 if t > 127 else t

    def accel(self, linear:bool=False, gravity:bool=False):
        """
        Read acceleration data from the BNO055 sensor.
        
        :param linear: If True, read linear acceleration (exclude gravity).
        :param gravity: If True, read gravity acceleration (exclude linear).
        :return: A tuple of acceleration values (x, y, z) in m/s².
        """
        if gravity:      reg = self.ACCEL_GRAVITY
        elif linear:     reg = self.ACCEL_LINEAR
        else:            reg = self.ACCELERATION
        return self.__read_vector(reg, 3, self.__SCALE[reg])

    def gyro(self):
        """
        Read gyroscope data from the BNO055 sensor.
        
        :return: A tuple of gyroscope values (x, y, z) in rad/s.
        """
        return self.__read_vector(self.GYROSCOPE, 3, self.__SCALE[self.GYROSCOPE])

    def mag(self):
        """
        Read magnetic field data from the BNO055 sensor.
        
        :return: A tuple of magnetic field values (x, y, z) in µT.
        """
        return self.__read_vector(self.MAGNETIC, 3, self.__SCALE[self.MAGNETIC])

    def euler(self):
        """
        Read Euler angles from the BNO055 sensor.
        
        :return: A tuple of Euler angles (heading, roll, pitch) in degrees.
        """
        return self.__read_vector(self.EULER, 3, self.__SCALE[self.EULER])

    def quaternion(self):
        """
        Read quaternion data from the BNO055 sensor.
        
        :return: A tuple of quaternion values (w, x, y, z).
        """
        return self.__read_vector(self.QUATERNION, 4, self.__SCALE[self.QUATERNION])

    def calibration(self):
        """
        Read the calibration status of the BNO055 sensor.
        The calibration status is returned as a tuple of four values: (system, gyro, accel, mag).
        
        :return: A tuple of calibration status values (system, gyro, accel, mag).
        """
        stat = self._i2c.read_u8(0x35)
        return (stat >> 6 & 3, stat >> 4 & 3, stat >> 2 & 3, stat & 3)

    def read(self, what):
        """
        Read data from the BNO055 sensor based on the specified register group.
        
        :param what: The register group to read from. It can be one of the following:
        - BNO055.TEMPERATURE
        - BNO055.ACCELERATION
        - BNO055.ACCEL_LINEAR
        - BNO055.ACCEL_GRAVITY
        - BNO055.GYROSCOPE
        - BNO055.MAGNETIC
        - BNO055.EULER
        - BNO055.QUATERNION
        :return: The data read from the specified register group.
        :raises ValueError: If the specified register group is unknown.
        """
        if what == self.TEMPERATURE:              return self.temperature()
        if what == self.ACCELERATION:             return self.accel()
        if what == self.ACCEL_LINEAR:             return self.accel(linear=True)
        if what == self.ACCEL_GRAVITY:            return self.accel(gravity=True)
        if what == self.GYROSCOPE:                return self.gyro()
        if what == self.MAGNETIC:                 return self.mag()
        if what == self.EULER:                    return self.euler()
        if what == self.QUATERNION:               return self.quaternion()
        raise ValueError("unknown register group")


class BME68x:
    def __init__(self, scl:int, sda:int, addr:int=0x77,
                 *,
                 temp_weighting=0.10,  pressure_weighting=0.05,
                 humi_weighting=0.20,  gas_weighting=0.65,
                 gas_ema_alpha=0.1,
                 temp_baseline=23.0,  pressure_baseline=1013.25,
                 humi_baseline=45.0,  gas_baseline=450_000):
        """
        A class to read data from the BME68x environmental sensor.
        This class provides methods to read temperature, pressure, humidity, and gas resistance data.
        
        :param scl: SCL pin number (GPIO pin)
        :param sda: SDA pin number (GPIO pin)
        :param addr: I2C address of the BME68x sensor (default is 0x77)
        :param temp_weighting: Weighting factor for temperature (default is 0.10)
        :param pressure_weighting: Weighting factor for pressure (default is 0.05)
        :param humi_weighting: Weighting factor for humidity (default is 0.20)
        :param gas_weighting: Weighting factor for gas resistance (default is 0.65)
        :param gas_ema_alpha: Exponential moving average alpha for gas resistance (default is 0.1)
        :param temp_baseline: Baseline temperature in degrees Celsius (default is 23.0)
        :param pressure_baseline: Baseline pressure in hPa (default is 1013.25)
        :param humi_baseline: Baseline humidity in % (default is 45.0)
        :param gas_baseline: Baseline gas resistance in ohms (default is 450000)
        """
        self._i2c = I2c(scl=scl, sda=sda, addr=addr)

        self._i2c.writeto_mem(0xE0, b'\xB6')      # soft-reset
        utime.sleep_ms(5)
        self._set_power_mode(0x00)                # sleep

        t_cal = bytearray(self._i2c.readfrom_mem(0x89, 25))
        t_cal += self._i2c.readfrom_mem(0xE1, 16)

        self._sw_err = (self._i2c.readfrom_mem(0x04, 1)[0] & 0xF0) >> 4

        calib = list(ustruct.unpack('<hbBHhbBhhbbHhhBBBHbbbBbHhbb',
                                    bytes(t_cal[1:39])))
        self._temp_calibration     = [calib[i] for i in (23, 0, 1)]
        self._pressure_calibration = [calib[i] for i in (3,4,5,7,8,10,9,12,13,14)]
        self._humidity_calibration = [calib[i] for i in (17,16,18,19,20,21,22)]

        self._humidity_calibration[1] = (
            self._humidity_calibration[1] * 16
            + self._humidity_calibration[0] % 16
        )
        self._humidity_calibration[0] //= 16

        self._i2c.writeto_mem(0x72, b'\x01')                # hum OSR x1
        self._i2c.writeto_mem(0x74, bytes([(0b010 << 5) | (0b011 << 2)]))
        self._i2c.writeto_mem(0x75, bytes([0b001 << 2]))    # IIR filter 3

        self._i2c.writeto_mem(0x50, b'\x1F')                # idac_heat_0
        self._i2c.writeto_mem(0x5A, b'\x73')                # res_heat_0
        self._i2c.writeto_mem(0x64, b'\x64')                # gas_wait_0 =100 ms

        self._i2c.writeto_mem(0x71, bytes([(1 << 4) | 0x00]))  # run_gas
        utime.sleep_ms(50)

        self._temperature_correction = -10
        self._t_fine = self._adc_pres = self._adc_temp = None
        self._adc_hum = self._adc_gas = self._gas_range = None

        self.temp_weighting     = temp_weighting
        self.pressure_weighting = pressure_weighting
        self.humi_weighting     = humi_weighting
        self.gas_weighting      = gas_weighting
        self.gas_ema_alpha      = gas_ema_alpha

        self.temp_baseline     = temp_baseline
        self.pressure_baseline = pressure_baseline
        self.humi_baseline     = humi_baseline
        self.gas_baseline      = gas_baseline

        if abs((temp_weighting   + pressure_weighting +
                humi_weighting   + gas_weighting) - 1.0) > 1e-3:
            raise ValueError("Weightings must sum to 1.0")

    def _set_power_mode(self, mode:int):
        """
        Set the power mode of the BME68x sensor.
        
        :param mode: The power mode to set (0x00 for sleep, 0x01 for forced, etc.).
        """
        reg = self._i2c.readfrom_mem(0x74, 1)[0] & ~0x03
        self._i2c.writeto_mem(0x74, bytes([reg | mode]))
        utime.sleep_ms(1)

    def _reset_sensor(self) -> bool:
        """
        Attempt to reset the BME68x sensor.
        This method tries to reset the sensor by writing to specific registers and checking the status.
        
        :return: True if the reset was successful, False otherwise.
        """
        self._i2c.writeto_mem(0xE0, b'\xB6')
        utime.sleep_ms(10)

        start = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), start) < 500:
            try:
                if self._i2c.readfrom_mem(0xD0, 1)[0] == 0x61:
                    # 재초기화
                    self._i2c.writeto_mem(0x72, b'\x01')
                    self._i2c.writeto_mem(0x74, bytes([(0b010 << 5) | (0b011 << 2)]))
                    self._i2c.writeto_mem(0x75, bytes([0b001 << 2]))
                    self._i2c.writeto_mem(0x50, b'\x1F')
                    self._i2c.writeto_mem(0x5A, b'\x73')
                    self._i2c.writeto_mem(0x64, b'\x64')
                    self._i2c.writeto_mem(0x71, bytes([(1 << 4) | 0x00]))
                    utime.sleep_ms(50)
                    return True
            except:
                pass
            utime.sleep_ms(10)
        return False

    def _perform_reading(self, retries:int=5):
        """
        Perform a reading from the BME68x sensor.
        This method attempts to read data from the sensor, retrying if necessary.
        
        :param retries: The number of retries to attempt if the reading fails (default is 5).
        """
        attempts, reset_done = 0, False
        while attempts < retries:
            attempts += 1
            try:
                self._i2c.writeto_mem(0x71, bytes([(1 << 4) | 0x00])) # forced mode (one-time measurement)
                self._set_power_mode(0x01)
                utime.sleep_ms(50)

                start = utime.ticks_ms()
                while utime.ticks_diff(utime.ticks_ms(), start) < 500:
                    s = self._i2c.readfrom_mem(0x1D, 1)[0]
                    if (s & 0x20) == 0 and (s & 0x80):
                        buf = self._i2c.readfrom_mem(0x1D, 17)
                        self._adc_pres = (buf[2] << 12) | (buf[3] << 4) | (buf[4] >> 4)
                        self._adc_temp = (buf[5] << 12) | (buf[6] << 4) | (buf[7] >> 4)
                        self._adc_hum  = (buf[8] << 8)  | buf[9]
                        self._adc_gas  = ((buf[13] << 2) | (buf[14] >> 6))
                        self._gas_range = buf[14] & 0x0F

                        # callculate temperature
                        v1 = (self._adc_temp / 8) - (self._temp_calibration[0] * 2)
                        v2 = (v1 * self._temp_calibration[1]) / 2048
                        v3 = ((v1 / 2) * (v1 / 2)) / 4096
                        v3 = (v3 * self._temp_calibration[2] * 16) / 16384
                        self._t_fine = int(v2 + v3)
                        return
                    utime.sleep_ms(10)

                if not reset_done and attempts >= (retries // 2):
                    reset_done = self._reset_sensor()
                    continue
            except:
                pass
            utime.sleep_ms(100 * attempts)
        raise OSError("BME68x: data not ready – power-cycle recommended")

    def _temperature(self) -> float:
        """
        Calculate the temperature in degrees Celsius.
        
        :return: The temperature in degrees Celsius.
        """
        return ((((self._t_fine * 5) + 128) / 256) / 100) + self._temperature_correction

    def _pressure(self) -> float:
        """
        Calculate the pressure in hPa.
        
        :return: The pressure in hPa.
        """
        v1 = (self._t_fine / 2) - 64000
        v2 = ((v1 / 4) ** 2) / 2048 * self._pressure_calibration[5] / 4
        v2 += (v1 * self._pressure_calibration[4] * 2)
        v2 = (v2 / 4) + (self._pressure_calibration[3] * 65536)
        v1 = (((((v1 / 4) ** 2) / 8192) * self._pressure_calibration[2] * 32) / 8 +
              (self._pressure_calibration[1] * v1) / 2) / 262144
        v1 = ((32768 + v1) * self._pressure_calibration[0]) / 32768
        p  = (1048576 - self._adc_pres - (v2 / 4096)) * 3125
        p  = (p / v1) * 2
        v1 = (self._pressure_calibration[8] * ((p / 8) ** 2) / 8192) / 4096
        v2 = ((p / 4) * self._pressure_calibration[7]) / 8192
        v3 = (((p / 256) ** 3) * self._pressure_calibration[9]) / 131072
        p += (v1 + v2 + v3 + (self._pressure_calibration[6] * 128)) / 16
        return p / 100

    def _humidity(self) -> float:
        """
        Calculate the relative humidity in percentage.
        
        :return: The relative humidity in percentage.
        """
        t = ((self._t_fine * 5) + 128) / 256
        v1 = (self._adc_hum - (self._humidity_calibration[0] * 16) -
              ((t * self._humidity_calibration[2]) / 200))
        v2 = (self._humidity_calibration[1] *
              (16384 + ((t * self._humidity_calibration[3]) / 100) +
               (((t * ((t * self._humidity_calibration[4]) / 100)) / 64) / 100))) / 1024
        v3 = v1 * v2
        v4 = (self._humidity_calibration[5] * 128 +
              ((t * self._humidity_calibration[6]) / 100)) / 16
        v5 = ((v3 / 16384) ** 2) / 1024
        v6 = (v4 * v5) / 2
        h  = ((((v3 + v6) / 1024) * 1000) / 4096) / 1000
        return max(0, min(h, 100))

    def _gas(self) -> float:
        """
        Calculate the gas resistance in ohms.
        
        :return: The gas resistance in ohms.
        """
        lookup1 = {0:2147483647.0,1:2126008810.0,2:2130303777.0,3:2147483647.0,
                   4:2143188679.0,5:2136746228.0,6:2126008810.0,7:2147483647.0}
        lookup2 = {0:4096000000.0,1:2048000000.0,2:1024000000.0,3:512000000.0,
                   4:255744255.0,5:127110228.0,6:64000000.0,7:32258064.0,
                   8:16016016.0,9:8000000.0,10:4000000.0,11:2000000.0,
                   12:1000000.0,13:500000.0,14:250000.0,15:125000.0}
        var1 = ((1340 + (5 * self._sw_err)) * lookup1.get(self._gas_range, 2**31-1)) / 65536
        var2 = (self._adc_gas * 32768) - 16777216 + var1
        var3 = (lookup2.get(self._gas_range, 125000.0) * var1) / 512
        return (var3 + (var2 / 2)) / var2

    def read(self, *, gas:bool=False):
        """
        Read sensor data from the BME68x sensor.
        
        :param gas: If True, include gas resistance in the reading.
        :return: A tuple containing temperature, pressure, humidity, and gas resistance (if requested).
        - T °C, P hPa, RH %, Gas Ω/None
        """
        self._perform_reading()
        if gas:
            return self._temperature(), self._pressure(), self._humidity(), self._gas()
        return self._temperature(), self._pressure(), self._humidity(), None

    def iaq(self):
        """
        Calculate the Indoor-Air-Quality (IAQ) score based on sensor readings.
        
        :return: A tuple containing the IAQ score (0-500) and sensor values (temperature, pressure, humidity, gas resistance).
        """
        self._perform_reading()
        t, p, h, g = self._temperature(), self._pressure(), self._humidity(), self._gas()

        hum_score  = (1 - min(abs(h - self.humi_baseline) / (self.humi_baseline*2), 1)) * self.humi_weighting * 100
        temp_score = (1 - min(abs(t - self.temp_baseline) / 10, 1)) * self.temp_weighting * 100

        self.gas_baseline = (self.gas_ema_alpha * g) + ((1 - self.gas_ema_alpha) * self.gas_baseline)
        gas_score = max(0, min((self.gas_baseline - g) / self.gas_baseline, 1)) * self.gas_weighting * 100

        press_score = (1 - min(abs(p - self.pressure_baseline) / 50, 1)) * self.pressure_weighting * 100

        iaq = round((hum_score + temp_score + gas_score + press_score) * 5)
        return iaq, t, p, h, g

