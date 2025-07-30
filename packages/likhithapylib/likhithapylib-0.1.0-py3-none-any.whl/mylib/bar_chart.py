import matplotlib.pyplot as plt

def bar_chart(categories, values, title='Bar Chart', xlabel='Categories', ylabel='Values'):
    plt.figure()
    plt.bar(categories, values, color='skyblue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y')
    plt.show()
