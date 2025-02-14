import math

# Takes the input angle and snaps it to the nearest multiple of the snap_angle.
# Converts input angle to degrees, snaps it, and returns the snapped angle in radians.
def snapping(input, snap_angle):
    input = math.degrees(snap_angle)  # Convert snap angle to degrees
    return math.radians(snap_angle * round(input / snap_angle))  # Snap the angle and convert back to radians

# Sets a specific bit (bitIndex) in the number n to 1.
# Uses bitwise OR to ensure the bit at bitIndex is set.
def setBit(n, bitIndex):
    bitMask = 1 << bitIndex  # Create a bitmask with the bit at bitIndex set to 1
    return n | bitMask  # Return the number with the bit set

# Takes a list of boolean flags and returns an integer with bits set
# based on the True values in the flag list. It starts with the given val (default 0).
def getFlagsVal(flag, val=0):
    for x in range(len(flag)):  # Loop through each flag
        if flag[x]:  # If the flag is True (bit should be set)
            val = setBit(val, x)  # Set the corresponding bit in val
    return val  # Return the resulting value with the appropriate bits set
