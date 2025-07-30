import matplotlib.pyplot as plt

def scatter_plot(x, y, title='Scatter Plot', xlabel='X-Axis', ylabel='Y-Axis'):
    plt.figure()
    plt.scatter(x, y, color='red')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.show()
