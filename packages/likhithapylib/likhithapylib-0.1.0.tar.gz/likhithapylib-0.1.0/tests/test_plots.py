import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mylib import line_plot, bar_chart, scatter_plot


def test_all():
    line_plot([1, 2, 3], [4, 5, 6], title="Test Line Plot")
    bar_chart(["A", "B", "C"], [5, 7, 3], title="Test Bar Chart")
    scatter_plot([1, 2, 3], [6, 2, 5], title="Test Scatter Plot")

# Run tests
if __name__ == "__main__":
    test_all()
