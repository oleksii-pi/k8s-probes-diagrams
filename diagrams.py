# diagrams/probe_diagrams.py
"""
This script generates 7 diagrams (Startup, Readiness, and Liveness probes)
to demonstrate how Kubernetes probes affect the lifespan of pods and traffic management.
Each diagram is saved in the "diagrams" folder with the following naming convention:
  - Startup Probes: 1.1-startup.png, 1.2-startup.png, 1.3-startup.png
  - Readiness Probes: 2.1-readiness.png, 2.2-readiness.png
  - Liveness Probes: 3.1-liveness.png, 3.2-liveness.png

The X-axis represents time in seconds (marked every 5 sec),
and the Y-axis represents probe outcome: 1 (True, OK/200) and 0 (False, Fail/503).
Each probe request is shown as a filled circle (green for success, red for failure).
Annotations indicate when Kubernetes makes decisions about the pod's status.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# Ensure the diagrams folder exists
os.makedirs("diagrams", exist_ok=True)

def setup_plot(x_max, title):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, x_max)
    ax.set_ylim(-0.2, 1.2)
    ax.set_xlabel("")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["False (503)", "True (200)"])
    ax.set_xticks(np.arange(0, x_max+1, 5))
    ax.set_title(title)
    return fig, ax

def plot_points(ax, times, statuses):
    # Plot each probe as a circle: green if True, red if False.
    for t, status in zip(times, statuses):
        color = 'green' if status == 1 else 'red'
        ax.scatter(t, status, color=color, s=100, zorder=3)

# -----------------------------------------
# 1. Startup Probe Configured
# -----------------------------------------
# Common startup probe config:
#   initialDelaySeconds: 5, periodSeconds: 2, failureThreshold: 30

# 1.1: App starts at 3 seconds => always ready when probe starts.
def diagram_1_1():
    title = "Startup Probe 1.1: App starts at 3 sec (pod becomes live at first probe)"
    # Probe times: start at 5 sec with period 2, let's show up to 15 sec.
    times = np.arange(5, 15, 2)
    # App started at 3 sec so every probe returns OK (True=1)
    statuses = [1 for _ in times]
    
    fig, ax = setup_plot(15, title)
    plot_points(ax, times, statuses)
    # Annotate the first success as pod live
    ax.annotate("Pod considered live", xy=(times[0], 1), xytext=(times[0]+1, 1.1),
                arrowprops=dict(arrowstyle="->", color='blue'))
    plt.tight_layout()
    fig.savefig("diagrams/1.1-startup.png")
    plt.close(fig)

# 1.2: App starts at 8 seconds => initial probes fail until app is live.
def diagram_1_2():
    title = "Startup Probe 1.2: App starts at 8 sec (pod becomes live when probe succeeds)"
    times = np.arange(5, 15, 2)  # probes at 5,7,9,11,13...
    statuses = []
    for t in times:
        # if probe time is >= app start time (8 sec), then OK.
        statuses.append(1 if t >= 8 else 0)
    
    fig, ax = setup_plot(15, title)
    plot_points(ax, times, statuses)
    # Annotate first success (at t=9 sec) as pod live.
    success_time = next(t for t, s in zip(times, statuses) if s==1)
    ax.annotate("Pod considered live", xy=(success_time, 1), xytext=(success_time+1, 1.1),
                arrowprops=dict(arrowstyle="->", color='blue'))
    plt.tight_layout()
    fig.savefig("diagrams/1.2-startup.png")
    plt.close(fig)

# 1.3: App starts at 90 seconds => never becomes live within failure threshold.
def diagram_1_3():
    title = "Startup Probe 1.3: App starts at 90 sec (pod killed after threshold failures)"
    # failureThreshold=30, so we have 30 consecutive failures.
    num_failures = 30
    times = np.arange(5, 5 + num_failures*2, 2)  # 5,7,9,... up to 63 sec
    statuses = [0 for _ in times]
    
    fig, ax = setup_plot(times[-1] + 5, title)
    plot_points(ax, times, statuses)
    # Annotate at the time of last allowed failure
    ax.annotate("k8s decides to kill pod", xy=(times[-1], 0), xytext=(times[-1]-10, -0.15),
                arrowprops=dict(arrowstyle="->", color='black'))
    plt.tight_layout()
    fig.savefig("diagrams/1.3-startup.png")
    plt.close(fig)

# -----------------------------------------
# 2. Readiness Probe Responses
# -----------------------------------------
# Readiness probe config:
#   initialDelaySeconds: 5, periodSeconds: 2, failureThreshold: 5

# 2.1: Ready endpoint returns OK for 10 sec, then 503 for 3 sec, then OK.
def diagram_2_1():
    title = "Readiness Probe 2.1: Temporary failure but pod remains ready"
    # Let's show from 5 to 17 seconds.
    times = np.arange(5, 18, 2)  # e.g., 5,7,9,11,13,15,17
    statuses = []
    for t in times:
        # Endpoint behavior: OK for t < 10, Fail for 10 <= t < 13, OK for t >= 13.
        if t < 10:
            statuses.append(1)
        elif 10 <= t < 13:
            statuses.append(0)
        else:
            statuses.append(1)
    
    fig, ax = setup_plot(18, title)
    plot_points(ax, times, statuses)
    # Even with a transient failure, k8s still routes traffic.
    ax.text(11, 0.5, "k8s considers pod always ready", color='purple')
    plt.tight_layout()
    fig.savefig("diagrams/2.1-readiness.png")
    plt.close(fig)

# 2.2: Ready endpoint returns OK for 10 sec, then 503 for 20 sec, then OK.
def diagram_2_2():
    title = "Readiness Probe 2.2: Extended failure changes traffic routing"
    # Let's simulate from 5 to 40 sec.
    times = np.arange(5, 41, 2)  # probes at 5,7,9,...,39
    statuses = []
    for t in times:
        # Endpoint: OK for t < 10, Fail for 10 <= t < 30, OK for t >= 30.
        if t < 10:
            statuses.append(1)
        elif 10 <= t < 30:
            statuses.append(0)
        else:
            statuses.append(1)
    
    fig, ax = setup_plot(40, title)
    plot_points(ax, times, statuses)
    # Readiness probe failureThreshold is 5.
    # After 5 consecutive failures (starting at t=11, 13, 15, 17, 19), pod becomes not ready.
    ax.annotate("k8s do not send traffic", xy=(19, 0), xytext=(19, -0.4),
                arrowprops=dict(arrowstyle="->", color='red'))
    # When a success is detected (at t=31), pod becomes ready again.
    ax.annotate("k8s sends traffic", xy=(31, 1), xytext=(31, 1.3),
                arrowprops=dict(arrowstyle="->", color='green'))
    plt.tight_layout()
    fig.savefig("diagrams/2.2-readiness.png")
    plt.close(fig)

# -----------------------------------------
# 3. Liveness Probe Responses
# -----------------------------------------
# Liveness probe config:
#   initialDelaySeconds: 10, periodSeconds: 2, failureThreshold: 5, terminationGracePeriodSeconds: 60

# 3.1: Live endpoint returns OK for 20 sec, then 503 for 5 sec, then OK.
def diagram_3_1():
    title = "Liveness Probe 3.1: Brief failure; pod remains live"
    # Probe times from 10 to 30 sec.
    times = np.arange(10, 31, 2)  # 10,12,14,16,18,20,22,24,26,28,30
    statuses = []
    for t in times:
        # Endpoint: OK for t < 20, Fail for 20 <= t < 25, OK for t >= 25.
        if t < 20:
            statuses.append(1)
        elif 20 <= t < 25:
            statuses.append(0)
        else:
            statuses.append(1)
    
    fig, ax = setup_plot(32, title)
    plot_points(ax, times, statuses)
    ax.text(20, 0.5, "Transient failure, pod remains live", color='purple')
    plt.tight_layout()
    fig.savefig("diagrams/3.1-liveness.png")
    plt.close(fig)

# 3.2: Live endpoint returns OK for 20 sec, then 503 continuously.
def diagram_3_2():
    title = "Liveness Probe 3.2: Extended failure leads to pod termination"
    # Probe times from 10 to 35 sec.
    times = np.arange(10, 36, 2)  # 10,12,14,16,18,20,22,24,26,28,30,32,34
    statuses = []
    for t in times:
        # Endpoint: OK for t < 20, Fail for t >= 20.
        statuses.append(1 if t < 20 else 0)
    
    fig, ax = setup_plot(40, title)
    plot_points(ax, times, statuses)
    # With failureThreshold=5, 5 consecutive failures occur at t=20,22,24,26,28.
    ax.annotate("k8s decides to kill the pod", xy=(28, 0), xytext=(25, -0.4),
                arrowprops=dict(arrowstyle="->", color='red'))
    # Termination grace period of 60 sec: annotate forced kill at t=28+60=88 sec.
    ax.annotate("Grace period starts", xy=(28, 0), xytext=(32, -0.6),
                arrowprops=dict(arrowstyle="->", color='black'))
    plt.tight_layout()
    fig.savefig("diagrams/3.2-liveness.png")
    plt.close(fig)

# -----------------------------------------
# Main: Generate all diagrams
# -----------------------------------------
def main():
    diagram_1_1()
    diagram_1_2()
    diagram_1_3()
    diagram_2_1()
    diagram_2_2()
    diagram_3_1()
    diagram_3_2()
    print("All diagrams have been saved in the 'diagrams' folder.")

if __name__ == "__main__":
    main()
