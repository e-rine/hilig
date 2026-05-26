ADJACENT_COST = 0.5
NORMAL_COST   = 1.0

KEYBOARD_ADJACENCY = {
    'q' : {'w', 'a', 's'},
    'w' : {'q', 'e', 'a', 's', 'd'},
    'e' : {'w', 'r', 's', 'd', 'f'},
    'r' : {'e', 't', 'd', 'f', 'g'},
    't' : {'r', 'y', 'f', 'g', 'h'},
    'y' : {'t', 'u', 'g', 'h', 'j'},
    'u' : {'y', 'i', 'h', 'j', 'k'},
    'i' : {'u', 'o', 'j', 'k', 'l'},
    'o' : {'i', 'p', 'k', 'l'},
    'p' : {'o', 'l'},
    'a' : {'q', 'w', 's', 'z'},
    's' : {'a', 'w', 'e', 'd', 'z', 'x'},
    'd' : {'s', 'e', 'r', 'f', 'x', 'c'},
    'f' : {'d', 'r', 't', 'g', 'c', 'v'},
    'g' : {'f', 't', 'y', 'h', 'v', 'b'},
    'h' : {'g', 'y', 'u', 'j', 'b', 'n'},
    'j' : {'h', 'u', 'i', 'k', 'n', 'm'},
    'k' : {'j', 'i', 'o', 'l', 'm'},
    'l' : {'k', 'o', 'p'},
    'z' : {'a', 's', 'x'},
    'x' : {'z', 's', 'd', 'c'},
    'c' : {'x', 'd', 'f', 'v'},
    'v' : {'c', 'f', 'g', 'b'},
    'b' : {'v', 'g', 'h', 'n'},
    'n' : {'b', 'h', 'j', 'm'},
    'm' : {'n', 'j', 'k'}
}


def subsitution_cost(x, y):
    if (x == y):
        return 0
    
    if (y in KEYBOARD_ADJACENCY.get(x, set())):
        return ADJACENT_COST
    return NORMAL_COST