

def clamp(val:int|float, lo:int|float, hi:int|float) -> int|float:
    """
    Clamps a value between a lower and upper bound.\r
\1 val: The value to be clamped.
    :param lo: The lower bound.
    :param hi: The upper bound.
    :return: The clamped value.
    """
    
def map(x:int|float, min_i:int|float, max_i:int|float, min_o:int|float, max_o:int|float) -> int|float:
    """
    Maps a value from one range to another.\r
\1 x: The value to be mapped.
    :param min_i: The minimum value of the input range.
    :param min_o: The minimum value of the output range.
    :return: The mapped value.
    """

def xrange(start: float, stop: float | None = None, step: float | None = None) -> iter[float]:
    """
    A generator function to create a range of floating point numbers.
    This is a replacement for the built-in range function for floating point numbers.   
    :param start: Starting value of the range.
    :param stop: Ending value of the range.
    :param step: Step size for the range.
    :return: A range object that generates floating point numbers.
    """

def rand(size:int=4) -> int:
    """
    Generates a random number of the specified size in bytes.\r
\1 size: The size of the random number in bytes. Default is 4 bytes.
    :return: A random number of the specified size.
    """

def intervalChecker(interval_ms:int) -> callable:
    """
    Creates a function that checks if the specified interval has passed since the last call.\r
\1 interval_ms: The interval in milliseconds.
    :return: A function that checks if the interval has passed.
    """


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

        @classmethod
        def down(cls, n:int) -> str:
            """
            Cursor down\r
\1 n: Number of lines to move down.
            :return: An ANSI escape code to move the cursor down.
            """
            
        @classmethod
        def right(cls, n:int) -> str:
            """
            Cursor right\r
\1 n: Number of columns to move right.
            :return: An ANSI escape code to move the cursor right.
            """

        @classmethod
        def left(cls, n:int) -> str:
            """
            Cursor left\r
\1 n: Number of columns to move left.
            :return: An ANSI escape code to move the cursor left.
            """
           
        @classmethod
        def next_line(cls, n:int) -> str:
            """
            Cursor down to next line\r
\1 n: Number of lines to move down.
            :return: An ANSI escape code to move the cursor down.
            """

        @classmethod
        def prev_line(cls, n:int) -> str:
            """
            Cursor up to previous line\r
\1 n: Number of lines to move up.
            :return: An ANSI escape code to move the cursor up.
            """
        
        @classmethod
        def to(cls, row:int, colum:int) -> str:
            """
            Move cursor to specified row and column.\r
\1 row: Row number (1-based).
            :param colum: Column number (1-based).
            :return: An ANSI escape code to move the cursor.
            """

 
class SlipEncoder:
    """
    SLIP Encoder class.
    This class is used to encode a byte array into a SLIP frame.
    The SLIP frame is a byte array that starts and ends with the END byte (0xC0).
    The ESC byte (0xDB) is used to escape the END and ESC bytes in the payload.
    The ESC byte is followed by ESC_END (0xDC) for END and ESC_ESC (0xDD) for ESC.
    """

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


class SlipDecoder:
    """
    SLIP Decoder class.
    This class is used to decode SLIP frames. It handles the decoding of the SLIP protocol,
    including escaping and unescaping bytes.
    """

    def __init__(self) -> None:
        """
        Initialize the SLIP decoder.
        This sets up the internal buffer and flags for processing SLIP frames.
        """

    def reset(self) -> None:
        """
        Reset the decoder state.
        This clears the buffer and resets the escape and in-frame flags.
        """

    def feed(self, chunk: bytes) -> list[bytes]:
        """
        Feed a chunk of bytes to the decoder.
        This processes the chunk and returns a list of complete SLIP frames.
        If the chunk contains incomplete frames, they will be buffered for the next call.\r
\1 chunk: The chunk of bytes to process.
        :return: A list of complete SLIP frames as byte arrays.
        """


class RingBuffer:
    """
    A simple ring buffer implementation for byte data.
    This class provides methods to put data into the buffer, get data from it,
    check available data, and peek for a specific pattern.
    """
    def __init__(self, size:int):
        """
        Initialize the ring buffer with a specified size.\r
\1 size: The size of the ring buffer.
        """

    def put(self, data:bytes):
        """
        Put data into the ring buffer.
        If the buffer is full, it will overwrite the oldest data.\r
\1 data: The data to put into the buffer (must be bytes).
        """

    def avail(self) -> int:
        """
        Check the number of available bytes in the ring buffer.
        
        :return: The number of bytes available in the buffer.
        """

    def get(self, n:int=1) -> bytes:
        """
        Get `n` bytes from the ring buffer.
        If `n` is greater than the available bytes, it will return only the available bytes.
        If `n` is None, it will return all available bytes.\r
\1 n: The number of bytes to get (default is 1).
        :return: The bytes read from the buffer.
        """
    
    def peek(self, n:int = 1) -> bytes:
        """
        Peek `n` bytes from the ring buffer without removing them.
        If `n` is greater than the available bytes, it will return only the available bytes.
        If `n` is None, it will return all available bytes.\r
\1 n: The number of bytes to peek (default is 1).
        :return: The bytes peeked from the buffer.
        """
        
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