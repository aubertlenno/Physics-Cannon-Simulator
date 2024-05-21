import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button, TextBox

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
hs = [2/5, 2/25, 2/25, 2/25, 2/25, 2/25, 1/5]
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

# Buttons:
axButton_launch = plt.subplot(gs[5, 4:])
button_launch = Button(ax=axButton_launch, label="Fire", color=bg_color, hovercolor=hc_color)

axButton_prev = plt.subplot(gs[4, 4:])
button_prev = Button(ax=axButton_prev, label="Save track", color=bg_color, hovercolor=hc_color)

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

plt.subplots_adjust(hspace=1)
plt.show()
