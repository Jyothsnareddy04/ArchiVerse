# =============================================================================
# ARCHITECTURAL BYLAWS ENGINE
# =============================================================================

from shapely.geometry import box

# =============================================================================
# DYNAMIC SETBACKS
# =============================================================================

def compute_setbacks(

    plot_width,
    plot_depth
):

    front = 5
    side = 4
    rear = 6

    # =============================================================
    # LARGE PLOTS
    # =============================================================

    if plot_width >= 50:

        side = 4.5

    if plot_width >= 65:

        side = 5

    if plot_depth >= 70:

        rear = 10

    elif plot_depth >= 55:

        rear = 8

    if plot_width >= 70:

        front = 8

    elif plot_width >= 50:

        front = 6

    return {

        "front": front,

        "side": side,

        "rear": rear
    }