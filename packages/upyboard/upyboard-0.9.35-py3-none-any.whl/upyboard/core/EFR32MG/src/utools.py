import uos
import utime


"""Clamp val into the inclusive range [lo, hi]."""
clamp = lambda val, lo, hi: lo if val < lo else hi if val > hi else val

"""map x from the range [min_i, max_i] to the range [min_o, max_o]."""
map = lambda x, min_i, max_i, min_o, max_o: (x - min_i) * (max_o - min_o) / (max_i - min_i) + min_o

def xrange(start: float, stop: float | None = None, step: float | None = None) -> iter[float]:
    """
    A generator function to create a range of floating point numbers.
    This is a replacement for the built-in range function for floating point numbers.   
    :param start: Starting value of the range.
    :param stop: Ending value of the range.
    :param step: Step size for the range.
    :return: A range object that generates floating point numbers.
    """
    
    if stop is None:
        stop, start = start, 0.0

    if step is None:
        step = 1.0 if stop >= start else -1.0

    if step == 0.0:
        raise ValueError("step must not be zero")

    if (stop - start) * step <= 0.0:
        return

    s_step = "{:.16f}".format(abs(step)).rstrip('0').rstrip('.')
    decimals = len(s_step.split('.')[1]) if '.' in s_step else 0

    idx = 0
    while True:
        value = start + idx * step
        if (step > 0 and value >= stop) or (step < 0 and value <= stop):
            break
        yield round(value, decimals)
        idx += 1

def rand(size:int=4) -> int:
    """
    Generates a random number of the specified size in bytes.\r
\1 size: The size of the random number in bytes. Default is 4 bytes.
    :return: A random number of the specified size.
    """
    
    return int.from_bytes(uos.urandom(size), "big")

def intervalChecker(interval_ms:int) -> callable:
    """
    Creates a function that checks if the specified interval has passed since the last call.\r
\1 interval_ms: The interval in milliseconds.
    :return: A function that checks if the interval has passed.
    """
    
    current_tick = utime.ticks_us()   
    
    def check_interval():
        nonlocal current_tick
        
        if utime.ticks_diff(utime.ticks_us(), current_tick) >= interval_ms * 1000:
            current_tick = utime.ticks_us()
            return True
        return False
    
    return check_interval


class ANSIEC:
    """
    ANSI Escape Codes for terminal text formatting.
    This class provides methods for setting foreground and background colors, as well as text attributes.
    It uses ANSI escape codes to format text in the terminal.
    """
    
    class FG:
        """
        ANSI escape codes for foreground colors.
        This class provides methods for setting foreground colors using ANSI escape codes.
        It includes standard colors, bright colors, and RGB color support.
        """
        
        BLACK = "\u001b[30m"
        RED = "\u001b[31m"
        GREEN = "\u001b[32m"
        YELLOW = "\u001b[33m"
        BLUE = "\u001b[34m"
        MAGENTA = "\u001b[35m"
        CYAN = "\u001b[36m"
        WHITE = "\u001b[37m"
        BRIGHT_BLACK= "\u001b[30;1m"
        BRIGHT_RED = "\u001b[31;1m"
        BRIGHT_GREEN = "\u001b[32;1m"
        BRIGHT_YELLOW = "\u001b[33;1m"
        BRIGHT_BLUE = "\u001b[34;1m"
        BRIGHT_MAGENTA = "\u001b[35;1m"
        BRIGHT_CYAN = "\u001b[36;1m"
        BRIGHT_WHITE = "\u001b[37;1m"
                
        @classmethod
        def rgb(cls, r:int, g:int, b:int) -> str:
            """
            Returns an ANSI escape code for RGB foreground color.
            :param r: Red component (0-255).
            :param g: Green component (0-255).
            :param b: Blue component (0-255).
            :return: An ANSI escape code for RGB foreground color.
            """
             
            return "\u001b[38;2;{};{};{}m".format(r, g, b)

    class BG:
        """
        ANSI escape codes for background colors.
        This class provides methods for setting background colors using ANSI escape codes.
        It includes standard colors, bright colors, and RGB color support.
        """
        
        BLACK = "\u001b[40m"
        RED = "\u001b[41m"
        GREEN = "\u001b[42m"
        YELLOW = "\u001b[43m"
        BLUE = "\u001b[44m"
        MAGENTA = "\u001b[45m"
        CYAN = "\u001b[46m"
        WHITE = "\u001b[47m"
        BRIGHT_BLACK= "\u001b[40;1m"
        BRIGHT_RED = "\u001b[41;1m"
        BRIGHT_GREEN = "\u001b[42;1m"
        BRIGHT_YELLOW = "\u001b[43;1m"
        BRIGHT_BLUE = "\u001b[44;1m"
        BRIGHT_MAGENTA = "\u001b[45;1m"
        BRIGHT_CYAN = "\u001b[46;1m"
        BRIGHT_WHITE = "\u001b[47;1m"
                
        @classmethod
        def rgb(cls, r:int, g:int, b:int) -> str:
            """
            Returns an ANSI escape code for RGB background color.\r
\1 r: Red component (0-255).
            :param g: Green component (0-255).
            :param b: Blue component (0-255).
            :return: An ANSI escape code for RGB background color.
            """
             
            return "\u001b[48;2;{};{};{}m".format(r, g, b)

    class OP:
        """
        A class for managing ANSI escape codes for font attributes and cursor positioning.
        This class provides methods to control font styles and cursor movement using ANSI escape codes.
        It supports actions such as resetting attributes, applying bold, underline, and reverse effects, clearing the screen or lines, and moving the cursor.
        """
        
        RESET = "\u001b[0m"
        BOLD = "\u001b[1m"
        UNDER_LINE = "\u001b[4m"
        REVERSE = "\u001b[7m"
        CLEAR = "\u001b[2J"
        CLEAR_LINE = "\u001b[2K"
        TOP = "\u001b[0;0H"

        @classmethod
        def up(cls, n:int) -> str:
            """
            Cursor up\r
\1 n: Number of lines to move up.
            :return: An ANSI escape code to move the cursor up.
            """
            return "\u001b[{}A".format(n)

        @classmethod
        def down(cls, n:int) -> str:
            """
            Cursor down\r
\1 n: Number of lines to move down.
            :return: An ANSI escape code to move the cursor down.
            """
            
            return "\u001b[{}B".format(n)

        @classmethod
        def right(cls, n:int) -> str:
            """
            Cursor right\r
\1 n: Number of columns to move right.
            :return: An ANSI escape code to move the cursor right.
            """
            
            return "\u001b[{}C".format(n)

        @classmethod
        def left(cls, n:int) -> str:
            """
            Cursor left\r
\1 n: Number of columns to move left.
            :return: An ANSI escape code to move the cursor left.
            """
            
            return "\u001b[{}D".format(n)
        
        @classmethod
        def next_line(cls, n:int) -> str:
            """
            Cursor down to next line\r
\1 n: Number of lines to move down.
            :return: An ANSI escape code to move the cursor down.
            """
            
            return "\u001b[{}E".format(n)

        @classmethod
        def prev_line(cls, n:int) -> str:
            """
            Cursor up to previous line\r
\1 n: Number of lines to move up.
            :return: An ANSI escape code to move the cursor up.
            """
            
            return "\u001b[{}F".format(n)
                
        @classmethod
        def to(cls, row:int, colum:int) -> str:
            """
            Move cursor to specified row and column.\r
\1 row: Row number (1-based).
            :param colum: Column number (1-based).
            :return: An ANSI escape code to move the cursor.
            """
            
            return "\u001b[{};{}H".format(row, colum)


class SlipEncoder:
    """
    SLIP Encoder class.
    This class is used to encode a byte array into a SLIP frame.
    The SLIP frame is a byte array that starts and ends with the END byte (0xC0).
    The ESC byte (0xDB) is used to escape the END and ESC bytes in the payload.
    The ESC byte is followed by ESC_END (0xDC) for END and ESC_ESC (0xDD) for ESC.
    """
    END      = 0xC0
    ESC      = 0xDB
    ESC_END  = 0xDC
    ESC_ESC  = 0xDD

    @staticmethod
    def encode(payload: bytes) -> bytes:
        """"
        Encode a byte array into a SLIP frame.
        The SLIP frame is a byte array that starts and ends with the END byte (0xC0).
        The ESC byte (0xDB) is used to escape the END and ESC bytes in the payload.
        The ESC byte is followed by ESC_END (0xDC) for END and ESC_ESC (0xDD) for ESC.\r
\1 payload: The byte array to encode.
        :return: The encoded SLIP frame as a byte array.
        """
        out = bytearray([SlipEncoder.END])       # leading END
        for b in payload:
            if b == SlipEncoder.END:
                out += bytes([SlipEncoder.ESC, SlipEncoder.ESC_END])
            elif b == SlipEncoder.ESC:
                out += bytes([SlipEncoder.ESC, SlipEncoder.ESC_ESC])
            else:
                out.append(b)
        out.append(SlipEncoder.END)              # trailing END
        return bytes(out)


class SlipDecoder:
    """
    SLIP Decoder class.
    This class is used to decode SLIP frames. It handles the decoding of the SLIP protocol,
    including escaping and unescaping bytes.
    """    
    END      = 0xC0
    ESC      = 0xDB
    ESC_END  = 0xDC
    ESC_ESC  = 0xDD

    def __init__(self) -> None:
        """
        Initialize the SLIP decoder.
        This sets up the internal buffer and flags for processing SLIP frames.
        """
        self._buf = bytearray()
        self._escaped = False
        self._in_frame = False

    def reset(self) -> None:
        """
        Reset the decoder state.
        This clears the buffer and resets the escape and in-frame flags.
        """
        self._buf[:] = b''
        self._escaped = False
        self._in_frame = False

    def feed(self, chunk: bytes) -> list[bytes]:
        """
        Feed a chunk of bytes to the decoder.
        This processes the chunk and returns a list of complete SLIP frames.
        If the chunk contains incomplete frames, they will be buffered for the next call.\r
\1 chunk: The chunk of bytes to process.
        :return: A list of complete SLIP frames as byte arrays.
        """
        frames = []
        for b in chunk:
            if self._escaped:
                if b == self.ESC_END:
                    self._buf.append(self.END)
                elif b == self.ESC_ESC:
                    self._buf.append(self.ESC)
                else:          # invalid escape
                    self.reset()
                    continue
                self._escaped = False
                continue

            if b == self.ESC:
                self._escaped = True
            elif b == self.END:
                if self._in_frame:
                    # END  frame 
                    frames.append(bytes(self._buf))
                    self._buf[:] = b''
                    self._in_frame = False
                else:
                    # junk end. start frame
                    self._in_frame = True
            else:
                if self._in_frame:
                    self._buf.append(b)
                # else: junk, byte invalied
        return frames


class RingBuffer:
    """
    A simple ring buffer implementation for byte data.
    This class provides methods to put data into the buffer, get data from it,
    check available data, and peek for a specific pattern.
    """
    def __init__(self, size:int):
        """
        Initialize the ring buffer with a specified size.\r
\1 size: The size of the ring buffer. (really size+1)
        """
        self._buf = bytearray(size)
        self._size = size
        self._head = 0
        self._tail = 0

    def put(self, data:bytes):
        """
        Put data into the ring buffer.
        If the buffer is full, it will overwrite the oldest data.\r
\1 data: The data to put into the buffer (must be bytes).
        """
        for b in data:
            nxt = (self._head + 1) % self._size
            if nxt == self._tail:
                self._tail = (self._tail + 1) % self._size
            self._buf[self._head] = b
            self._head = nxt

    def avail(self) -> int:
        """
        Check the number of available bytes in the ring buffer.
        
        :return: The number of bytes available in the buffer.
        """
        return (self._head - self._tail) % self._size

    def get(self, n:int=1) -> bytes:
        """
        Get `n` bytes from the ring buffer.
        If `n` is greater than the available bytes, it will return only the available bytes.
        If `n` is None, it will return all available bytes.\r
\1 n: The number of bytes to get (default is 1).
        :return: The bytes read from the buffer.
        """
        n = min(n, self.avail())
        out = self._buf[self._tail:self._tail + n] \
            if self._tail + n <= self._size else \
            self._buf[self._tail:] + self._buf[:(self._tail+n)%self._size]
        self._tail = (self._tail + n) % self._size
        return bytes(out)

    def peek(self, n:int = 1) -> bytes:
        """
        Peek `n` bytes from the ring buffer without removing them.
        If `n` is greater than the available bytes, it will return only the available bytes.
        If `n` is None, it will return all available bytes.\r
\1 n: The number of bytes to peek (default is 1).
        :return: The bytes peeked from the buffer.
        """
        n = min(n, self.avail())
        if n == 0:
            return b''

        if self._tail + n <= self._size:
            return bytes(self._buf[self._tail:self._tail + n])

        part1 = self._buf[self._tail:]
        part2 = self._buf[:(self._tail + n) % self._size]
        return bytes(part1 + part2)
    
    def get_until(self, pattern:bytes, max_size:int|None=None) -> bytes|None:
        """
        Peek for a specific pattern in the ring buffer.
        Searches for the first occurrence of `pattern` in the buffer.
        If `max_size` is specified, it will return at most `max_size` bytes.
        If the pattern is not found, it returns None.\r
\1 pattern: The byte sequence to search for.
        :param max_size: The maximum size of data to return (default is None, no limit).
        :return: The bytes up to the pattern if found, otherwise None.
        """
        plen = len(pattern)
        total = self.avail()
        if total < plen:
            return None

        view = self.peek(total) 
        idx  = view.find(pattern)
        if idx == -1:
            return None 

        length = idx + plen
        if max_size and length > max_size:
            length = max_size

        return self.get(length)