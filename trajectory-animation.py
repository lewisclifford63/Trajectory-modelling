import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Gravitational constant
G = 6.67430e-11

# Function to calculate acceleration due to gravity
def gravitational_acceleration(t, y, M_blackhole):
    x, y, z, vx, vy, vz = y
    r = np.sqrt(x**2 + y**2 + z**2)
    ax = -G * M_blackhole * x / r**3
    ay = -G * M_blackhole * y / r**3
    az = -G * M_blackhole * z / r**3
    return [vx, vy, vz, ax, ay, az]

# Function to simulate the trajectory
def simulate_trajectory(initial_position, initial_velocity, M_blackhole, T, num_points):
    # Initial conditions: [x, y, z, vx, vy, vz]
    y0 = initial_position + initial_velocity

    # Time span and time evaluation points
    t_span = (0, T)
    t_eval = np.linspace(0, T, num_points)  # Time points for simulation
    
    # Solve the system of differential equations
    sol = solve_ivp(gravitational_acceleration, t_span, y0, args=(M_blackhole,), 
                    t_eval=t_eval, method='RK45')

    return sol.t, sol.y

# Parameters
M_blackhole = 1.989e30  # Mass of black hole (kg)
initial_position = [1.5e11, 0, 0]  # Initial position (1 AU from black hole)
initial_velocity = [0, 3e4, 0]  # Initial velocity (Earth's orbital speed)
T = 3.154e8  # Time span (10 years in seconds, larger T for longer orbit)
num_points = 10000  # Increase number of points for better accuracy over long time

# Simulate the trajectory
times, positions = simulate_trajectory(initial_position, initial_velocity, M_blackhole, T, num_points)

# Extract the position data
x_data, y_data, z_data = positions[0], positions[1], positions[2]

# Create the figure and 3D axis for the plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Set the labels for the axes
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('3D Orbit of Planet Around Black Hole')

# Initialize the plot with an empty trajectory line and planet marker
trajectory_line, = ax.plot([], [], [], lw=2, color='blue', label='Trajectory')
planet_marker, = ax.plot([], [], [], 'ro', markersize=8, label='Planet')

# Draw the black hole at the origin
ax.scatter(0, 0, 0, color='black', s=100, label='Black Hole')

# Set the plot limits (adjust based on your orbit size)
ax.set_xlim([-2e11, 2e11])
ax.set_ylim([-2e11, 2e11])
ax.set_zlim([-2e10, 2e10])

# Initialize the animation
def init():
    trajectory_line.set_data([], [])
    trajectory_line.set_3d_properties([])
    planet_marker.set_data([], [])
    planet_marker.set_3d_properties([])
    return trajectory_line, planet_marker

# Update function for the animation
def update(frame):
    # Update the trajectory line to include all points up to the current frame
    trajectory_line.set_data(x_data[:frame], y_data[:frame])
    trajectory_line.set_3d_properties(z_data[:frame])

    # Update the position of the planet
    planet_marker.set_data([x_data[frame]], [y_data[frame]])
    planet_marker.set_3d_properties([z_data[frame]])

    return trajectory_line, planet_marker

# Number of frames in the animation (reduce frames to speed up animation)
frame_skip = 30  # This means every 30th point is rendered
num_frames = len(times) // frame_skip

# Create the animation, setting interval to control the speed
ani = FuncAnimation(fig, update, frames=range(0, len(times), frame_skip), init_func=init, interval=20, blit=True)

# Save the animation as a GIF file
# ani.save('static/animation.gif', writer='pillow', fps=30)

plt.show()
