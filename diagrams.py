import os
import numpy as np
import matplotlib.pyplot as plt

# Ensure diagrams folder exists
os.makedirs("diagrams", exist_ok=True)

def plot_diagram(time_points, responses, title, annotations, filename, x_max=None):
    """
    Plots a step diagram showing probe responses over time.
    - time_points: array of times when probes are sent.
    - responses: corresponding list of response values (0 for Fail, 1 for OK).
    - title: title of the plot.
    - annotations: list of dicts with keys 'time', 'text', and optional 'color'
      used to draw vertical lines and text for key events.
    - filename: output file name (saved under "diagrams").
    - x_max: maximum x-axis value (if None, computed from time_points).
    """
    plt.figure(figsize=(10, 4))
    # Plot as a step function (using 'post' to show the value after each probe time)
    plt.step(time_points, responses, where='post', linewidth=2)
    plt.ylim(-0.2, 1.2)
    plt.yticks([0, 1], ['Fail (503)', 'OK (200)'])
    if x_max is None:
        x_max = time_points[-1] + 5
    plt.xlim(0, x_max)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Probe Response")
    plt.title(title)
    plt.xticks(np.arange(0, x_max+1, 5))
    
    # Draw vertical lines and add text annotations
    for ann in annotations:
        color = ann.get('color', 'red')
        plt.axvline(x=ann['time'], color=color, linestyle='--')
        plt.text(ann['time'] + 0.5, 1.05, ann['text'], rotation=90,
                 verticalalignment='bottom', color=color)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join("diagrams", filename))
    plt.close()

# ------------------------------------------------------------------------------
# 1. Startup Probe Configured
# ------------------------------------------------------------------------------

def startup_probe_1_1():
    """
    1.1. App starts in 3 seconds.
         - Probes (startup probe with initialDelay=5, period=2) are sent at 5, 7, 9, …
         - Since the app started at 3s, the first probe at 5s returns OK.
    """
    time_points = np.arange(5, 26, 2)  # simulate from 5 to 25 seconds
    responses = [1] * len(time_points)  # all responses are OK (1)
    annotations = [
        {'time': 3, 'text': 'App Start (3s)', 'color': 'green'},
        {'time': 5, 'text': 'k8s considers live', 'color': 'blue'}
    ]
    title = "Startup Probe - App starts at 3 seconds"
    filename = "startup_probe_app_start_3.png"
    plot_diagram(time_points, responses, title, annotations, filename, x_max=30)

def startup_probe_1_2():
    """
    1.2. App starts in 8 seconds.
         - Probes at t=5 and t=7 occur before the app is live (returns Fail, 0).
         - At t=9 the app is live (since 8s < 9s), so probe returns OK.
    """
    time_points = np.arange(5, 26, 2)
    responses = [0 if t < 9 else 1 for t in time_points]
    annotations = [
        {'time': 8, 'text': 'App Start (8s)', 'color': 'green'},
        {'time': 9, 'text': 'k8s considers live', 'color': 'blue'}
    ]
    title = "Startup Probe - App starts at 8 seconds"
    filename = "startup_probe_app_start_8.png"
    plot_diagram(time_points, responses, title, annotations, filename, x_max=30)

def startup_probe_1_3():
    """
    1.3. App starts in 90 seconds.
         - The probe continues to fail. With failureThreshold=30 (period=2),
           the 30th consecutive failure occurs at t = 5 + 29*2 = 63 seconds.
         - Although the app would start at 90s, k8s kills the pod at 63s.
    """
    time_points = np.arange(5, 70, 2)  # simulate up to ~70 seconds
    responses = [0] * len(time_points)
    annotations = [
        {'time': 90, 'text': 'App Start (90s)', 'color': 'green'},
        {'time': 63, 'text': 'k8s decides to kill pod', 'color': 'red'}
    ]
    title = "Startup Probe - App starts at 90 seconds (Pod Killed)"
    filename = "startup_probe_app_start_90.png"
    plot_diagram(time_points, responses, title, annotations, filename, x_max=75)

# ------------------------------------------------------------------------------
# 2. Startup Probe Not Configured – Using Readiness Probe Responses
# ------------------------------------------------------------------------------

def readiness_probe_2_1():
    """
    2.1. Ready endpoint:
         - Returns OK for 20 seconds, then 503 for 3 seconds, then OK for 5 seconds.
         - With failureThreshold=5, the short failure (only two consecutive failures)
           does not mark the pod as not ready.
         - k8s considers the pod always ready (traffic continues to be sent).
    """
    time_points = np.arange(5, 36, 2)  # simulate from 5 to 35 seconds
    responses = []
    for t in time_points:
        if 5 <= t < 25:
            responses.append(1)
        elif 25 <= t < 29:
            responses.append(0)
        else:
            responses.append(1)
    annotations = [
        {'time': 5, 'text': 'Readiness probe starts', 'color': 'purple'},
        {'time': 25, 'text': 'Start Failures', 'color': 'red'},
        {'time': 29, 'text': 'Recovery', 'color': 'blue'}
    ]
    title = "Readiness Probe - Transient Failures (Always Ready)"
    filename = "readiness_probe_always_ready.png"
    plot_diagram(time_points, responses, title, annotations, filename, x_max=40)

def readiness_probe_2_2():
    """
    2.2. Ready endpoint:
         - Returns OK for 20 seconds, then 503 for 20 seconds, then OK for 5 seconds.
         - With 5 consecutive failures (starting at t=25, at t=33 the threshold is met),
           k8s marks the pod as not ready (stop sending traffic).
         - When the endpoint returns OK again (at t=45), the pod is marked ready.
    """
    time_points = np.arange(5, 56, 2)  # simulate from 5 to 55 seconds
    responses = []
    for t in time_points:
        if 5 <= t < 25:
            responses.append(1)
        elif 25 <= t < 45:
            responses.append(0)
        else:
            responses.append(1)
    annotations = [
        {'time': 5, 'text': 'Readiness probe starts', 'color': 'purple'},
        {'time': 33, 'text': 'Marked Not Ready', 'color': 'red'},
        {'time': 45, 'text': 'Ready Again', 'color': 'blue'}
    ]
    title = "Readiness Probe - Prolonged Failures (Not Ready then Ready)"
    filename = "readiness_probe_not_ready.png"
    plot_diagram(time_points, responses, title, annotations, filename, x_max=60)

# ------------------------------------------------------------------------------
# 3. Liveness Probe Responses
# ------------------------------------------------------------------------------

def liveness_probe_3_1():
    """
    3.1. Live endpoint:
         - Returns OK for 20 seconds, then 503 for 5 seconds, then OK again.
         - With failureThreshold=5, the brief failure (3 consecutive failures) does not
           trigger a pod restart.
         - k8s continues to consider the pod live.
    """
    time_points = np.arange(10, 41, 2)  # liveness probes start at 10 seconds
    responses = []
    for t in time_points:
        if 10 <= t < 30:
            responses.append(1)
        elif 30 <= t < 35:
            responses.append(0)
        else:
            responses.append(1)
    annotations = [
        {'time': 10, 'text': 'Liveness probe starts', 'color': 'purple'},
        {'time': 30, 'text': 'Start transient failures', 'color': 'red'},
        {'time': 35, 'text': 'Recovery', 'color': 'blue'}
    ]
    title = "Liveness Probe - Transient Failures (Always Live)"
    filename = "liveness_probe_always_live.png"
    plot_diagram(time_points, responses, title, annotations, filename, x_max=45)

def liveness_probe_3_2():
    """
    3.2. Live endpoint:
         - Returns OK for 20 seconds, then 503 for 15 seconds.
         - Probes (starting at t=10 with period=2) will see failures at t=30,32,34,36,38.
         - With failureThreshold=5, at t=38 the pod is marked not live and a kill is initiated.
         - With terminationGracePeriodSeconds=60, the pod is forcibly killed at t=38+60 = 98 seconds.
    """
    time_points = np.arange(10, 100, 2)  # simulate from 10 to 98+ seconds
    responses = []
    for t in time_points:
        if 10 <= t < 30:
            responses.append(1)
        elif 30 <= t < 40:
            responses.append(0)
        else:
            responses.append(1)  # after kill decision, state is moot
    annotations = [
        {'time': 10, 'text': 'Liveness probe starts', 'color': 'purple'},
        {'time': 38, 'text': 'Marked Not Live & Kill Initiated', 'color': 'red'},
        {'time': 98, 'text': 'Grace Period End (Forced Kill)', 'color': 'black'}
    ]
    title = "Liveness Probe - Prolonged Failures (Pod Killed)"
    filename = "liveness_probe_kill.png"
    plot_diagram(time_points, responses, title, annotations, filename, x_max=105)

# ------------------------------------------------------------------------------
# Main – Generate all diagrams
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    startup_probe_1_1()
    startup_probe_1_2()
    startup_probe_1_3()
    readiness_probe_2_1()
    readiness_probe_2_2()
    liveness_probe_3_1()
    liveness_probe_3_2()
    print("Diagrams created in the 'diagrams' folder.")
