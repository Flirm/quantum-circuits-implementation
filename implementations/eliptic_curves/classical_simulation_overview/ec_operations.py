


class ECurve:

    def __init__(self, a, b, p):
        assert (4*(a**3) + 27(b**2)) != 0, "Elliptic curve parameters not valid (4a^3 + 27b^2 = 0)"
        self.a = a
        self.b = b
        self.p = p


class Point:
    def __init__(self, x, y, curve: ECurve, is_inf = False):
        self.x = x
        self.y = y
        self.curve = curve
        self.is_inf = is_inf
        assert (y**2 == x**3 + curve.a*x + curve.b) or is_inf, "Point not on elliptic curve"

    def inv_mod(self, k):
        p = self.curve.p
        def extended_gcd(a, b):
            if b == 0:
                return a, 1, 0
            gcd, x1, y1 = extended_gcd(b, a % b)
            x = y1
            y = x1 - (a // b) * y1
            return gcd, x, y

        gcd, x, _ = extended_gcd(k, p)
        if gcd != 1:
            raise ValueError("Inverse does not exist")
        return x % p

    def negative(self):
        return Point(self.x, -self.y % self.curve.p)
    
    def point_add(self, q: "Point"):
        assert self.curve == q.curve, "Points on different curves"
        
        if self.is_inf:
            return q
        if q.is_inf: 
            return self
        
        if self.x == q.x and self.y != q.y:
            return Point(0,0,self.curve, True)
        
        if self.x == q.x:
            lamb = (3*(self.x**2) + self.curve.a) * self.inv_mod(2*q.y)
        else:
            lamb = (q.y - self.y) * self.inv_mod(q.x - self.x,)
        
        x = lamb**2 - self.x - q.x
        y = lamb*(self.x - x) - self.y

        return Point(x, y, self.curve)

    def point_multiply(self, k):
        assert k>=1, "K < 1"

        final = Point(0, 0, self.curve, True)
        intermediate = Point(self.x, self.y, self.curve, self.is_inf)

        if k&1:
            final = self.point_add(final)
        k = k>>1

        while k:
            intermediate = intermediate.point_add(intermediate)

        final = final.point_add(intermediate)

        return final
            
