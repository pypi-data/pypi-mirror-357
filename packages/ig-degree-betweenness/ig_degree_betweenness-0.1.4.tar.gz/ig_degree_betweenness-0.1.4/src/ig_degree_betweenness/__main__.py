"""Allow ig_degree_betweenness to be executable through `python -d ig_degree_betweenness edgelist.txt`."""

import sys
from ig_degree_betweenness import core

if __name__ == "__main__":
    core.main()
