from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

G = 6.67430e-11  # Gravitational constant

# Function to calculate acceleration due to gravity
def gravitational_acceleration(t, y, M_blackhole):
    x, y, z, vx, vy, vz = y
    r = np.sqrt(x**2 + y**2 + z**2)
    ax = -G * M_blackhole * x / r**3
    ay = -G * M_blackhole * y / r**3
    az = -G * M_blackhole * z / r**3
    return [vx, vy, vz, ax, ay, az]

# Simulate the orbit trajectory
def simulate_trajectory(initial_position, initial_velocity, M_blackhole, T, num_points):
    # Initial conditions: [x, y, z, vx, vy, vz]
    y0 = initial_position + initial_velocity
    t_span = (0, T)
    t_eval = np.linspace(0, T, num_points)
    
    # Solve the system of differential equations
    sol = solve_ivp(gravitational_acceleration, t_span, y0, args=(M_blackhole,), t_eval=t_eval, method='RK45')
    return sol.t, sol.y

@app.route('/')
def index():
    # Render the HTML page where the placeholder GIF is shown first
    return render_template('index.html')

@app.route('/start_animation', methods=['POST'])
def start_animation():
    data = request.json
    M_blackhole = float(data['bh_mass']) * 1e30  # Convert black hole mass to kg
    initial_position = data['position']  # [x, y, z] position vector
    initial_velocity = data['velocity']  # [vx, vy, vz] velocity vector

    # Parameters for the simulation
    T = 3.154e8  # Time span (10 years in seconds)
    num_points = 10000  # Number of points for accuracy

    # Simulate the trajectory
    times, positions = simulate_trajectory(initial_position, initial_velocity, M_blackhole, T, num_points)

    # Extract the position data
    x_data, y_data, z_data = positions[0], positions[1], positions[2]

    # Create frames for the animation and return them as base64 encoded strings
    frames = []
    frame_skip = 30  # Skip frames to speed up animation generation
    num_frames = len(x_data) // frame_skip

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Set plot limits
    ax.set_xlim([-2e11, 2e11])
    ax.set_ylim([-2e11, 2e11])
    ax.set_zlim([-2e10, 2e10])
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title('3D Orbit of Planet Around Black Hole')

    trajectory_line, = ax.plot([], [], [], lw=2, color='blue', label='Trajectory')
    planet_marker, = ax.plot([], [], [], 'ro', markersize=8, label='Planet')
    ax.scatter(0, 0, 0, color='black', s=100, label='Black Hole')

    # Update function for the animation
    def update(frame):
        trajectory_line.set_data(x_data[:frame], y_data[:frame])
        trajectory_line.set_3d_properties(z_data[:frame])
        planet_marker.set_data([x_data[frame]], [y_data[frame]])
        planet_marker.set_3d_properties([z_data[frame]])

        # Save the frame as an image in memory (not on disk)
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
        frames.append(plot_url)

    # Generate the frames
    for frame in range(0, num_frames):
        update(frame * frame_skip)

    plt.close(fig)  # Close the plot to free up memory

    # Return the frames as a JSON response
    return jsonify({'frames': frames})

if __name__ == '__main__':
    app.run(debug=True)
