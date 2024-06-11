import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button, TextBox
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox as mbox

# Colors:
bg_color = "#cbc5b3"
hc_color = "#cbc5b3"
main_color_1 = "#71b1d0"
main_color_2 = "#71b1d0"
saved_color = "#ff7f0e"  # Color for saved trajectories

plt.style.use('Solarize_Light2')

fig = plt.figure()
fig.patch.set_facecolor("#d9d3c0")
fig.suptitle("CannonLab", fontsize=14, fontweight="bold")
fig.canvas.manager.set_window_title("CannonLab")

# Proportions:
hs = [15/50, 15/50, 5/50, 5/50, 5/50, 5/50]  # Adjusted to make top bars taller
ws = [1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8]

gs = GridSpec(ncols=8, nrows=6, width_ratios=ws, height_ratios=hs, figure=fig)

# Top Bars:
ax_impulses = plt.subplot(gs[0, :3], facecolor=bg_color)
impulse_bar = ax_impulses.bar(["Projectile", "Cannon (1)", "Cannon (2)"], [0, 0, 0], color=main_color_1)
plt.xlabel("Impulses, kg*m/s")
plt.grid(True)

ax_forces = plt.subplot(gs[0, 3:6], facecolor=bg_color)
force_bar = ax_forces.bar(["Friction C", "Reaction C", "Gravity P"], [0, 0, 0], color=main_color_1)
plt.xlabel("Forces, N")
plt.grid(True)

ax_velocities = plt.subplot(gs[0, 6:], facecolor=bg_color)
velocity_bar = ax_velocities.bar(["Initial P", "X-coordinate P", "Initial C"], [0, 0, 0], color=main_color_1)
plt.xlabel("Velocities, m/s")
plt.grid(True)

# Main plane:
ax = plt.subplot(gs[1:, :], facecolor=bg_color)
ax.set_aspect("auto")

plt.xlabel("x, m")
plt.ylabel("y, m")
plt.grid(True)

def add_value_labels(ax, bars):
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height / 2,
            f'{height:.2f}',
            ha='center',
            va='center',
            color='black',
            fontsize=12,
            fontweight='bold'
        )

# Initial values and constants
angle_grad = 45  # °
efficiency = 30  # %
gunpowder = 10  # g
target_height, target_x, hit_y = 20, 450, 0  # m
g = 9.8  # m/s^2
x0, y0 = 0, 0  # starting point
q = 3800  # J/g
M = 100  # kg
m = 5  # kg

r_wheel = 0.3
friction_coef = 0.45

# Air resistance parameters
air_density = 1.225  # kg/m^3
drag_coefficient = 0.47  # dimensionless, spherical projectile
cross_sectional_area = 0.05  # m^2, example value

# Control for air resistance
apply_air_resistance = True

angle = 0
initial_speed = 0
time_interval = 0
x_offset = 0
y_offset = 0

x_prev_data, y_prev_data = [], []

show_prev_track = False
hit_check = False

# To store multiple trajectories
trajectories = []

anim = None  # Ensuring the animation object is not deleted

def compute_drag_force(v):
    return 0.5 * air_density * v**2 * drag_coefficient * cross_sectional_area

def compute_position_with_drag(t):
    global x_offset, y_offset, angle, initial_speed, m, g

    dt = 0.1  # time step
    x, y = x_offset, y_offset
    vx, vy = initial_speed * np.cos(angle), initial_speed * np.sin(angle)

    for _ in np.arange(0, t, dt):
        v = np.sqrt(vx**2 + vy**2)
        if apply_air_resistance:
            drag_force = compute_drag_force(v)
            ax_drag = drag_force * (vx / v) / m
            ay_drag = drag_force * (vy / v) / m
        else:
            ax_drag = ay_drag = 0

        vx -= ax_drag * dt
        vy -= (g + ay_drag) * dt

        x += vx * dt
        y += vy * dt

        if y < 0:
            break

    return x, y

def compute_x(t, track="bullet"):
    if track == "bullet":
        x, _ = compute_position_with_drag(t)
        return x
    elif track == "cannon":
        global x_offset, angle, initial_speed, friction_coef, r_wheel, m, M, g
        deceleration = compute_force(force="friction") / M
        if np.cos(angle) * initial_speed * (m / M) > deceleration * t:
            return x_offset - np.cos(angle) * initial_speed * (m / M) * t + deceleration * (t ** 2) / 2
        else:
            return x_offset - ((np.cos(angle) * initial_speed * (m / M)) ** 2) / (2 * deceleration)

def compute_y(t, track="bullet"):
    if track == "bullet":
        _, y = compute_position_with_drag(t)
        return y
    elif track == "cannon":
        global y_offset
        return y_offset

def compute_force(mass="m", force="friction"):
    global friction_coef, m, M, g, r_wheel

    if force == "friction":
        return friction_coef * M * g / r_wheel
    elif force == "gravity":
        if mass == "m":
            return m * g
        elif mass == "M":
            return M * g

def compute_impulse(t=0, track="bullet"):
    global initial_speed, friction_coef, M, m, g

    if track == "bullet":
        return initial_speed * m
    elif track == "cannon":
        return max(0.0, initial_speed * m - compute_force(force="friction") * t)

def clear_track():
    for line in ax.get_lines():
        line.remove()

    # Re-plot saved trajectories with a distinct color and style
    for traj in trajectories:
        ax.plot(traj['x'], traj['y'], "--", color=saved_color, lw=2)

def update_config():
    global angle, initial_speed, time_interval, x_offset, y_offset, target_height, target_x, hit_y

    angle = angle_grad * np.pi / 180
    initial_speed = np.sqrt((2 * efficiency * q * gunpowder) / (100 * m))
    time_interval = (np.sin(angle) * initial_speed + np.sqrt(
        (np.sin(angle) * initial_speed) ** 2 + 2 * g * y0)) / g
    x_offset = x0
    y_offset = y0

    if compute_x(time_interval, track="bullet") >= target_x:
        t_hit = (target_x - x_offset) / (np.cos(angle) * initial_speed)
        hit_y = compute_y(t_hit, track="bullet")

    return np.arange(0, time_interval, 0.1)

def plot_target():
    global target_x, target_height

    ax.plot([target_x, target_x], [0, target_height], color=main_color_1, lw=3)

def plot_bars():
    global time_interval, initial_speed, angle

    y_impulses_data = [compute_impulse(track="bullet"), compute_impulse(track="cannon"),
                       compute_impulse(t=time_interval, track="cannon")]

    y_forces_data = [compute_force(force="friction"), compute_force(mass="M", force="gravity"),
                     compute_force(mass="m", force="gravity")]

    y_velocities_data = [initial_speed, np.cos(angle) * initial_speed, np.cos(angle) * initial_speed * (m / M)]

    ax_impulses.clear()
    ax_forces.clear()
    ax_velocities.clear()

    impulse_bar = ax_impulses.bar(["Projectile", "Cannon (1)", "Cannon (2)"], y_impulses_data, color=main_color_1)
    force_bar = ax_forces.bar(["Friction C", "Reaction C", "Gravity P"], y_forces_data, color=main_color_1)
    velocity_bar = ax_velocities.bar(["Initial P", "X-coordinate P", "Initial C"], y_velocities_data, color=main_color_1)

    add_value_labels(ax_impulses, impulse_bar)
    add_value_labels(ax_forces, force_bar)
    add_value_labels(ax_velocities, velocity_bar)

def stop_animation():
    global anim
    if anim:
        anim.event_source.stop()

def run_animation():
    global x_prev_data, y_prev_data, anim

    current_trajectory_x, current_trajectory_y = [], []  # Reset current trajectory

    def update_track(t):
        global target_x, target_height, hit_y, hit_check

        x_bullet = compute_x(t, track="bullet")
        y_bullet = compute_y(t, track="bullet")

        x_cannon = compute_x(t, track="cannon")
        y_cannon = compute_y(t, track="cannon")

        if x_bullet not in current_trajectory_x:
            current_trajectory_x.append(x_bullet)
            current_trajectory_y.append(y_bullet)

            if target_x <= x_bullet and hit_y <= target_height and hit_check:
                ax.plot([target_x], [hit_y], "o", mfc=main_color_2, mec=main_color_2, markersize=8)
                hit_check = False

            bullet_track.set_data(current_trajectory_x, current_trajectory_y)

        if x_cannon not in x_data["cannon"]:
            x_data["cannon"].append(x_cannon)
            y_data["cannon"].append(y_cannon)

            cannon_track.set_data(x_data["cannon"], y_data["cannon"])

        ax.relim()
        ax.autoscale_view(scalex=True, scaley=True)

    bullet_track, = ax.plot([], [], color=main_color_2, lw=3)
    cannon_track, = ax.plot([], [], color=main_color_1, lw=3)

    x_data, y_data = {"cannon": [], "bullet": []}, {"cannon": [], "bullet": []}

    x_prev_data = current_trajectory_x
    y_prev_data = current_trajectory_y

    anim = FuncAnimation(fig, func=update_track, frames=update_config(), interval=20, blit=False)

def launch(event):
    global hit_check

    stop_animation()  # Stop any existing animation
    hit_check = True
    clear_track()  # This will now re-plot saved trajectories
    plot_target()
    plot_bars()
    run_animation()
    plt.draw()  # Ensure the plot is updated

def save_trajectory(event):
    global x_prev_data, y_prev_data, trajectories
    stop_animation()  # Stop any existing animation
    if x_prev_data and y_prev_data:
        trajectories.append({"x": x_prev_data.copy(), "y": y_prev_data.copy()})
        plt.draw()

def clear_trajectories(event):
    global trajectories
    stop_animation()  # Stop any existing animation
    trajectories.clear()
    clear_track()
    plt.draw()

def toggle_air_resistance(event):
    global apply_air_resistance
    stop_animation()  # Stop any existing animation
    apply_air_resistance = not apply_air_resistance
    if apply_air_resistance:
        button_toggle_air_resistance.label.set_text("Air Resistance: ON")
    else:
        button_toggle_air_resistance.label.set_text("Air Resistance: OFF")
    plt.draw()

def open_modal():
    stop_animation()  # Stop any existing animation

    def on_submit():
        global angle_grad, gunpowder, efficiency, x0, y0, target_x, target_height, m, M
        try:
            angle_grad = int(entry_angle.get())
            gunpowder = int(entry_gunpowder.get())
            efficiency = int(entry_efficiency.get())
            x0 = int(entry_x0.get())
            y0 = int(entry_y0.get())
            target_x = int(entry_target_x.get())
            target_height = int(entry_target_height.get())
            m = int(entry_m.get())
            M = int(entry_M.get())
        except ValueError:
            mbox.showerror("Cannon Firing Setup", "Incorrect measure format")
        modal.destroy()

    modal = tk.Toplevel(root)
    modal.title("Input Parameters")

    tk.Label(modal, text="Angle, °").grid(row=0, column=0)
    entry_angle = tk.Entry(modal)
    entry_angle.insert(0, angle_grad)
    entry_angle.grid(row=0, column=1)

    tk.Label(modal, text="Gunpowder, g").grid(row=1, column=0)
    entry_gunpowder = tk.Entry(modal)
    entry_gunpowder.insert(0, gunpowder)
    entry_gunpowder.grid(row=1, column=1)

    tk.Label(modal, text="Efficiency, %").grid(row=2, column=0)
    entry_efficiency = tk.Entry(modal)
    entry_efficiency.insert(0, efficiency)
    entry_efficiency.grid(row=2, column=1)

    tk.Label(modal, text="Starting point X, m").grid(row=3, column=0)
    entry_x0 = tk.Entry(modal)
    entry_x0.insert(0, x0)
    entry_x0.grid(row=3, column=1)

    tk.Label(modal, text="Starting point Y, m").grid(row=4, column=0)
    entry_y0 = tk.Entry(modal)
    entry_y0.insert(0, y0)
    entry_y0.grid(row=4, column=1)

    tk.Label(modal, text="Target X, m").grid(row=5, column=0)
    entry_target_x = tk.Entry(modal)
    entry_target_x.insert(0, target_x)
    entry_target_x.grid(row=5, column=1)

    tk.Label(modal, text="Target height, m").grid(row=6, column=0)
    entry_target_height = tk.Entry(modal)
    entry_target_height.insert(0, target_height)
    entry_target_height.grid(row=6, column=1)

    tk.Label(modal, text="Projectile mass, kg").grid(row=7, column=0)
    entry_m = tk.Entry(modal)
    entry_m.insert(0, m)
    entry_m.grid(row=7, column=1)

    tk.Label(modal, text="Cannon mass, kg").grid(row=8, column=0)
    entry_M = tk.Entry(modal)
    entry_M.insert(0, M)
    entry_M.grid(row=8, column=1)

    tk.Button(modal, text="Submit", command=on_submit).grid(row=9, columnspan=2)

root = tk.Tk()
root.withdraw()  # Hide the root window

axButton_modal = plt.axes([0.7, 0.02, 0.1, 0.04])
button_modal = Button(axButton_modal, 'Input Params')
button_modal.on_clicked(lambda event: open_modal())

axButton_launch = plt.axes([0.8, 0.02, 0.1, 0.04])
button_launch = Button(axButton_launch, 'Fire')
button_launch.on_clicked(launch)

axButton_save_trajectory = plt.axes([0.4, 0.02, 0.1, 0.04])
button_save_trajectory = Button(axButton_save_trajectory, 'Save Shot')
button_save_trajectory.on_clicked(save_trajectory)

axButton_clear_trajectories = plt.axes([0.3, 0.02, 0.1, 0.04])
button_clear_trajectories = Button(axButton_clear_trajectories, 'Clear Shots')
button_clear_trajectories.on_clicked(clear_trajectories)

axButton_toggle_air_resistance = plt.axes([0.5, 0.02, 0.1, 0.04])
button_toggle_air_resistance = Button(axButton_toggle_air_resistance, 'Air Resistance: ON')
button_toggle_air_resistance.on_clicked(toggle_air_resistance)

plt.subplots_adjust(hspace=1)
plt.show()
