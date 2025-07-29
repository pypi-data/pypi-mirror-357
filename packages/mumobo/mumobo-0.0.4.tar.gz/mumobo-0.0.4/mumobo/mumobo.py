import socket
import time
import sys

class MuMoBo:
    """
    Client for communicating with MuMoBo microcontrollers over a persistent TCP socket.

    This class sends control commands (e.g., ping, move, change ID) to servos grouped by axis
    via a TCP socket connection to a microcontroller server. It maintains a persistent connection
    and parses newline-terminated, comma-separated responses into lists of integers.

    Attributes
    ----------
    host : str
        Hostname or IP address of the target microcontroller server.
    port : int
        Port number on which the server listens.
    timeout : float
        Socket timeout in seconds for connect and receive operations.
    verbose : bool
        Whether to print detailed logs during communication.
    client_socket : socket.socket or None
        The active socket object (if connected).
    response_buffer : str
        Internal buffer for accumulating incoming data.
    """

    def __init__(self, host: str, port: int = 80, timeout: float = 20.0, verbose: bool = False):
        """
        Initialize the MuMoBo client with connection parameters.

        Parameters
        ----------
        host : str
            Target server hostname or IP.
        port : int, optional
            Server port (default is 80).
        timeout : float, optional
            Timeout for socket operations in seconds.
        verbose : bool, optional
            Enables verbose printing for debugging.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        self.client_socket = None
        self.response_buffer = ''

    def _connect(self):
        """
        Establish a TCP connection if not already connected.

        Raises
        ------
        ConnectionError
            If the socket connection fails.
        """
        if self.client_socket is not None:
            return
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(self.timeout)
            self.client_socket.connect((self.host, self.port))
            if self.verbose:
                print(f"Connected to {self.host}:{self.port}")
        except Exception as e:
            self.client_socket = None
            raise ConnectionError(f"Failed to connect: {e}")

    def _close_socket(self):
        """
        Close the active socket cleanly, if it exists.
        """
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.client_socket.close()
            self.client_socket = None
            if self.verbose:
                print("Socket closed.")

    def _send_numbers(self, mode, axis, sID, nID, position):
        """
        Send a formatted command to the server and collect response lines.

        Parameters
        ----------
        mode : int
            Command mode (e.g., 0 = ping, 1 = change ID).
        axis : int
            Axis identifier (typically 1 or 2).
        sID : int
            Source servo ID.
        nID : int
            New servo ID (if applicable).
        position : int
            Step count or position offset.

        Returns
        -------
        list of list of int
            Parsed integer responses received from the server.
        """
        data = f'{mode},{axis},{sID},{nID},{position}\n'
        messages = []
        try:
            self._connect()
            self.client_socket.sendall(data.encode('utf-8'))
            if self.verbose:
                print(f"Sent: {data.strip()}")

            self.client_socket.settimeout(0.5)
            self.response_buffer = ''
            last_data_time = time.time()
            max_idle = 0.05

            while time.time() - last_data_time < max_idle:
                try:
                    response = self.client_socket.recv(1024).decode('utf-8')
                    if not response:
                        break
                    last_data_time = time.time()
                    self.response_buffer += response
                    while '\n' in self.response_buffer:
                        complete, self.response_buffer = self.response_buffer.split('\n', 1)
                        if complete.strip() != 'Server response:':
                            try:
                                values = [int(x) for x in complete.strip().split(',')]
                                messages.append(values)
                            except ValueError:
                                print("Invalid number in message")
                except socket.timeout:
                    pass

        except (ConnectionError, socket.error) as e:
            if self.verbose:
                print(f"Communication error: {e}")
            self._close_socket()
        except Exception as e:
            print(f"Unexpected error: {e}")
            self._close_socket()

        return messages

    def ping(self, AXIS, SERVO_ID):
        """
        Ping a servo to check if it is responsive.

        Parameters
        ----------
        AXIS : int
            The axis on which the servo resides (1 or 2).
        SERVO_ID : int
            ID of the target servo.

        Returns
        -------
        list of list of int or None
            Parsed response if successful, otherwise None.
        """
        if AXIS in (1, 2) and 1 <= SERVO_ID < 254:
            return self._send_numbers(0, AXIS, SERVO_ID, 0, 0)
        else:
            print("Error: invalid axis or servo ID")

    def scan(self, AXIS, start: int = 1, stop: int = 253):
        """
        Scan for all available servo IDs on the given axis.

        Parameters
        ----------
        AXIS : int
            The axis to scan.
        start : int, optional
            Starting servo ID (inclusive).
        stop : int, optional
            Ending servo ID (inclusive).

        Returns
        -------
        list of int
            List of servo IDs that responded to a ping.
        """
        if AXIS in (1, 2):
            available = []
            for i in self._progress_bar(range(start, stop + 1), prefix="Scanning: "):
                response = self.ping(AXIS, i)
                if response and response[0][0] == 0:
                    available.append(i)
            return available
        else:
            print("Error: invalid axis")

    def changeID(self, AXIS, SERVO_ID, NEW_ID):
        """
        Change the ID of a given servo.

        Parameters
        ----------
        AXIS : int
            Target axis.
        SERVO_ID : int
            Current ID of the servo.
        NEW_ID : int
            New ID to assign.

        Returns
        -------
        list of list of int or None
            Server response, if any.
        """
        if AXIS in (1, 2) and 1 <= SERVO_ID < 254:
            return self._send_numbers(1, AXIS, SERVO_ID, NEW_ID, 0)
        else:
            print("Error: invalid axis or servo ID")

    def step_Mode(self, AXIS, SERVO_ID):
        """
        Put a servo into step mode (for relative movements).

        Parameters
        ----------
        AXIS : int
            Axis of the servo.
        SERVO_ID : int
            ID of the servo.

        Returns
        -------
        list of list of int
            Response from the server.
        """
        return self._send_numbers(2, AXIS, SERVO_ID, 0, 0)

    def move_motor_by(self, AXIS, SERVO_ID, STEPS):
        """
        Move a servo by a given number of steps.

        Parameters
        ----------
        AXIS : int
            Axis of the servo.
        SERVO_ID : int
            ID of the servo.
        STEPS : int
            Number of steps to move (positive or negative).

        Returns
        -------
        list of list of int or None
            Server response or None if input invalid.
        """
        if AXIS in (1, 2):
            if abs(STEPS) < 3 * 4096:
                return self._send_numbers(3, AXIS, SERVO_ID, 0, STEPS)
            else:
                print('Error: Step too large.')
        else:
            print('Error: Invalid axis.')

    def close(self):
        """
        Manually close the socket connection.
        """
        self._close_socket()

    def __del__(self):
        """
        Ensure socket is closed on object deletion.
        """
        self._close_socket()

    def _progress_bar(self, iterable, total=None, prefix='', length=40):
        """
        Display a minimal progress bar with ETA using only the standard library.

        Parameters
        ----------
        iterable : iterable
            The iterable to loop through.
        total : int, optional
            Total number of items (inferred from iterable if not given).
        prefix : str, optional
            Prefix string for the progress bar.
        length : int, optional
            Width of the progress bar.

        Yields
        ------
        item
            Each item from the iterable.
        """
        total = total or len(iterable)
        start_time = time.time()
        for i, item in enumerate(iterable, 1):
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            eta = avg_time * (total - i)

            done = int(length * i / total)
            bar = '=' * done + ' ' * (length - done)
            sys.stdout.write(
                f'\r{prefix}[{bar}] {i}/{total} ETA: {int(eta)}s'
            )
            sys.stdout.flush()
            yield item
        print()
