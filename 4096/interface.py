#!/usr/bin/env python3
import engine, sys, uuid, random, subprocess, socket, os

if len(sys.argv) < 3:
	sys.stderr.write("Usage: interface.py <randomseed> <executable>\n")
	sys.exit()

# set up seed from arguments
random.seed(sys.argv[1])

# helpers for writing and reading to the socket connection
def write(conn, str):
	conn.send(str.encode("utf-8"))

def read(conn):
	return conn.recv(1024).decode("utf-8").strip()

# create local unix socket for communication with child
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
identifier = str(uuid.uuid4())
s_path = "/tmp/4096-" + identifier
s.bind(s_path)

# launch child
process = subprocess.Popen([sys.argv[2], s_path])
s.listen(1)
conn, addr = s.accept()

# set up engine and game meta information
game = engine.Engine()
move_count = 0
game_name = read(conn)

sys.stderr.write("Game: " + game_name + "\n")
sys.stderr.write("Identifier: " + identifier + "\n")

# give client board and process input until finished
write(conn, game.to_string())

try:
	while conn:
		c = read(conn)

		if c == 'u':
			game.up()
		elif c == 'd':
			game.down()
		elif c == 'l':
			game.left()
		elif c == 'r':
			game.right()

		write(conn, game.to_string())

		move_count += 1

		if game.is_board_locked():
			write(conn, "FIN " + str(game.score) + "\n")
except (BrokenPipeError, ConnectionResetError):
	# give score
	sys.stderr.write("Score: " + str(game.score) + "\n")
	sys.stderr.write("Moves: " + str(move_count) + "\n")

# clean up
process.terminate()
os.remove(s_path)
