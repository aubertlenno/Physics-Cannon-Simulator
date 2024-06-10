import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button, TextBox
from matplotlib.animation import FuncAnimation
from tkinter import messagebox as mbox

# Colors:
bg_color = "#cbc5b3"
hc_color = "#cbc5b3"
main_color_1 = "#8dd3c7"
main_color_2 = "#71b1d0"

plt.style.use('Solarize_Light2')

fig = plt.figure()
fig.patch.set_facecolor("#d9d3c0")
fig.suptitle("CannonLab", fontsize=14, fontweight="bold")
fig.canvas.manager.set_window_title("CannonLab")

# Proportions:
hs = [25/50, 3/50, 3/50, 3/50, 3/50, 3/50, 10/50]
ws = [1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8]

gs = GridSpec(ncols=8, nrows=7, width_ratios=ws, height_ratios=hs, figure=fig)

# Main plane:
ax = plt.subplot(gs[0, :8], facecolor=bg_color)
ax.set_aspect("auto")

plt.xlabel("x, m")
plt.ylabel("y, m")
plt.grid(True)

# Bars:
ax_impulses = plt.subplot(gs[6, :3], facecolor=bg_color)
impulse_bar = ax_impulses.bar(["Projectile", "Cannon (1)", "Cannon (2)"], [0, 0, 0], color=main_color_1)
plt.xlabel("Impulses, kg*m/s")
plt.grid(True)

ax_forces = plt.subplot(gs[6, 3:6], facecolor=bg_color)
force_bar = ax_forces.bar(["Friction C", "Reaction C", "Gravity P"], [0, 0, 0], color=main_color_1)
plt.xlabel("Forces, N")
plt.grid(True)

ax_velocities = plt.subplot(gs[6, 6:], facecolor=bg_color)
velocity_bar = ax_velocities.bar(["Initial P", "X-coordinate P", "Initial C"], [0, 0, 0], color=main_color_1)
plt.xlabel("Velocities, m/s")
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

angle = 0
initial_speed = 0
time_interval = 0
x_offset = 0
y_offset = 0

x_prev_data, y_prev_data = [], []

show_prev_track = False
hit_check = False

def compute_x(t, track="bullet"):
    global x_offset, angle, initial_speed, friction_coef, r_wheel, m, M, g

    if track == "bullet":
        return x_offset + np.cos(angle) * initial_speed * t
    elif track == "cannon":
        deceleration = compute_force(force="friction") / M
        if np.cos(angle) * initial_speed * (m / M) > deceleration * t:
            return x_offset - np.cos(angle) * initial_speed * (m / M) * t + deceleration * (t ** 2) / 2
        else:
            return x_offset - ((np.cos(angle) * initial_speed * (m / M)) ** 2) / (2 * deceleration)

def compute_y(t, track="bullet"):
    global y_offset, angle, initial_speed, g

    if track == "bullet":
        return y_offset + np.sin(angle) * initial_speed * t - g * (t ** 2) / 2
    elif track == "cannon":
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
    global x_prev_data, y_prev_data

    for line in ax.get_lines():
        line.remove()

    if show_prev_track:
        ax.plot(x_prev_data, y_prev_data, "--", color=hc_color, lw=3)

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

global anim  # Ensuring the animation object is not deleted
def run_animation():
    global x_prev_data, y_prev_data, anim

    def update_track(t):
        global target_x, target_height, hit_y, hit_check

        x_bullet = compute_x(t, track="bullet")
        y_bullet = compute_y(t, track="bullet")

        x_cannon = compute_x(t, track="cannon")
        y_cannon = compute_y(t, track="cannon")

        if x_bullet not in x_data["bullet"]:
            x_data["bullet"].append(x_bullet)
            y_data["bullet"].append(y_bullet)

            if target_x <= x_bullet and hit_y <= target_height and hit_check:
                ax.plot([target_x], [hit_y], "o", mfc=main_color_2, mec=main_color_2, markersize=8)
                hit_check = False

            bullet_track.set_data(x_data["bullet"], y_data["bullet"])

        if x_cannon not in x_data["cannon"]:
            x_data["cannon"].append(x_cannon)
            y_data["cannon"].append(y_cannon)

            cannon_track.set_data(x_data["cannon"], y_data["cannon"])

        ax.relim()
        ax.autoscale_view(scalex=True, scaley=True)

    bullet_track, = ax.plot([], [], color=main_color_2, lw=3)
    cannon_track, = ax.plot([], [], color=main_color_1, lw=3)

    x_data, y_data = {"cannon": [], "bullet": []}, {"cannon": [], "bullet": []}

    x_prev_data = x_data["bullet"]
    y_prev_data = y_data["bullet"]

    anim = FuncAnimation(fig, func=update_track, frames=update_config(), interval=20, blit=False)

def launch(event):
    global hit_check

    hit_check = True
    clear_track()
    plot_target()
    plot_bars()
    run_animation()

def update_prev(event):
    global show_prev_track

    if show_prev_track:
        show_prev_track = False
        button_prev.label.set_text("Save previous track")
    else:
        show_prev_track = True
        button_prev.label.set_text("Omit previous track")

def update_angle(val):
    global angle_grad
    angle_grad = slider_angle.val

def update_gunpowder(val):
    global gunpowder
    gunpowder = slider_gunpowder.val

def update_efficiency(val):
    global efficiency
    efficiency = slider_efficiency.val

def check_format(label, positive_only=False):
    try:
        value = int(label)
        if (not positive_only and value >= 0) or value > 0:
            return True
        else:
            mbox.showerror("Cannon Firing Setup", "Incorrect measure format")
            return False
    except ValueError:
        mbox.showerror("Cannon Firing Setup", "Incorrect measure format")
        return False

def update_x0(label):
    global x0
    if check_format(label):
        x0 = int(label)

def update_y0(label):
    global y0
    if check_format(label):
        y0 = int(label)

def update_target_x(label):
    global target_x
    if check_format(label):
        target_x = int(label)

def update_target_height(label):
    global target_height
    if check_format(label):
        target_height = int(label)

def update_bullet_m(label):
    global m
    if check_format(label, positive_only=True):
        m = int(label)

def update_cannon_m(label):
    global M
    if check_format(label, positive_only=True):
        M = int(label)

# Buttons:
axButton_launch = plt.subplot(gs[5, 4:])
button_launch = Button(ax=axButton_launch, label="Fire", color=bg_color, hovercolor=hc_color)

axButton_prev = plt.subplot(gs[4, 4:6])
button_prev = Button(ax=axButton_prev, label="Save track", color=bg_color, hovercolor=hc_color)

axButton_load = plt.subplot(gs[4, 6:])
button_load = Button(ax=axButton_load, label="Load track", color=bg_color, hovercolor=hc_color)

button_launch.on_clicked(launch)
button_prev.on_clicked(update_prev)

# Sliders:
axSlider_angle = plt.subplot(gs[1, :4])
slider_angle = Slider(ax=axSlider_angle, label="Angle, °", valmin=1, valmax=89, valinit=45, valstep=1, initcolor=None, color="darkolivegreen",
                      track_color=hc_color)

axSlider_gunpowder = plt.subplot(gs[2, :4])
slider_gunpowder = Slider(ax=axSlider_gunpowder, label="Gunpowder, g", valmin=10, valmax=100, valstep=10, initcolor=None, color="darkolivegreen",
                          track_color=hc_color)

axSlider_efficiency = plt.subplot(gs[3, :4])
slider_efficiency = Slider(ax=axSlider_efficiency, label="Efficiency, %", valmin=1, valmax=100, valstep=1, valinit=30,
                           initcolor=None, color="darkolivegreen", track_color=hc_color)

slider_angle.on_changed(update_angle)
slider_gunpowder.on_changed(update_gunpowder)
slider_efficiency.on_changed(update_efficiency)

# Text boxes:
axTextBox_x_start = plt.subplot(gs[4, :2])
axTextBox_x_start.set_title("Starting point X", fontsize=12)
textbox_x_start = TextBox(ax=axTextBox_x_start, label="X, m", initial="0", textalignment="center", color=bg_color,
                          hovercolor=hc_color)

axTextBox_y_start = plt.subplot(gs[4, 2:4])
axTextBox_y_start.set_title("Starting point Y", fontsize=12)
textbox_y_start = TextBox(ax=axTextBox_y_start, label="Y, m", initial="0", textalignment="center", color=bg_color,
                          hovercolor=hc_color)

axTextBox_target_x = plt.subplot(gs[5, :2])
axTextBox_target_x.set_title("Target X", fontsize=12)
textbox_target_x = TextBox(ax=axTextBox_target_x, label="X, m", initial="450", textalignment="center", color=bg_color,
                           hovercolor=hc_color)

axTextBox_target_height = plt.subplot(gs[5, 2:4])
axTextBox_target_height.set_title("Target height", fontsize=12)
textbox_target_height = TextBox(ax=axTextBox_target_height, label="H, m", initial="20", textalignment="center",
                                color=bg_color, hovercolor=hc_color)

axTextBox_bullet_m = plt.subplot(gs[1, 5:])
axTextBox_bullet_m.set_title("Projectile mass:", fontsize=12)
textbox_bullet_m = TextBox(ax=axTextBox_bullet_m, label="m, kg", initial="5", textalignment="center", color=bg_color,
                           hovercolor=hc_color)

axTextBox_cannon_m = plt.subplot(gs[2, 5:])
axTextBox_cannon_m.set_title("Cannon mass:", fontsize=12)
textbox_cannon_m = TextBox(ax=axTextBox_cannon_m, label="M, kg", initial="100", textalignment="center", color=bg_color,
                           hovercolor=hc_color)

textbox_x_start.on_submit(update_x0)
textbox_y_start.on_submit(update_y0)
textbox_target_x.on_submit(update_target_x)
textbox_target_height.on_submit(update_target_height)
textbox_bullet_m.on_submit(update_bullet_m)
textbox_cannon_m.on_submit(update_cannon_m)

plt.subplots_adjust(hspace=1)
plt.show()
