import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from joblib import Parallel, delayed
import multiprocessing

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

# Function to simulate a segment of the trajectory
def simulate_segment(t_start, t_end, y0, M_blackhole):
    t_span = (t_start, t_end)
    sol = solve_ivp(gravitational_acceleration, t_span, y0, args=(M_blackhole,), 
                    t_eval=np.linspace(t_start, t_end, 1000), method='RK45')
    return sol.t, sol.y

# Main simulation function using parallel processing
def parallel_simulation(initial_position, initial_velocity, M_blackhole, T, num_segments):
    # Split the total time span into smaller segments
    time_segments = np.linspace(0, T, num_segments + 1)

    # Initialize the state with the initial conditions
    y0 = initial_position + initial_velocity
    
    # Store the results
    times = []
    positions = []
    
    # Iterate over the segments (we can't parallelize the initial condition transition between segments)
    for i in range(num_segments):
        t_start = time_segments[i]
        t_end = time_segments[i + 1]
        # Solve this segment
        t_segment, y_segment = simulate_segment(t_start, t_end, y0, M_blackhole)
        
        # Append the results for this segment
        times.append(t_segment)
        positions.append(y_segment)
        
        # Update the initial condition for the next segment
        y0 = [y_segment[0][-1], y_segment[1][-1], y_segment[2][-1],   # Position (x, y, z)
              y_segment[3][-1], y_segment[4][-1], y_segment[5][-1]]   # Velocity (vx, vy, vz)
    
    # Concatenate all the time and position data
    times = np.concatenate(times)
    positions = np.hstack(positions)
    
    return times, positions

# Parameters
M_blackhole = 1.989e30  # Mass of black hole (kg)
M_planet = 5.972e24  # Mass of planet (kg)
initial_position = [1.5e11, 0, 0]  # Initial position (1 AU from black hole)
initial_velocity = [0, 3e4, 0]  # Initial velocity (roughly Earth's orbital speed)
T = 3.154e7  # Time span (1 year in seconds)
num_segments = 10  # Divide the simulation into 10 segments

# Simulate the trajectory
times, positions = parallel_simulation(initial_position, initial_velocity, M_blackhole, T, num_segments)

# Extract the position data
x, y, z = positions[0], positions[1], positions[2]

# Plot the 3D trajectory
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot(x, y, z, label="Planet Trajectory", color="blue")
ax.scatter(0, 0, 0, color="black", label="Black Hole", s=100)  # Black hole at the origin

ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title("3D Trajectory of Planet around Black Hole")
plt.legend()

plt.show()
