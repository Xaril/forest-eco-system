def Lerp(min, max, fraction):
    return min + (max - min) * fraction

def InverseLerp(min, max, number):
    return (number - min)/ (max - min)
