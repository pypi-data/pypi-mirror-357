import matplotlib.pyplot as plt

def line_plot(x, y, title='Line Plot', xlabel='X-Axis', ylabel='Y-Axis'):
    plt.figure()
    plt.plot(x, y, marker='o', linestyle='-', color='blue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.show()
