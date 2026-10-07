"""README / video thumbnail (a still):  python -m manim -qh -s thumbnail.py Thumbnail"""
from motifs import *  # noqa: F401,F403


class Thumbnail(Scene):
    def construct(self):
        title = T(r"The Haldane gap,", font_size=78)
        title2 = T(r"proved?", font_size=78, color=GAP)
        head = VGroup(title, title2).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        sub = T(r"one partition function, read two ways", font_size=38, color=DIM)
        sub.next_to(head, DOWN, aligned_edge=LEFT, buff=0.5)
        left = VGroup(head, sub).to_edge(LEFT, buff=0.7).shift(UP * 0.3)

        tor = Torus(4.4, 2.8, nx=10, ny=6)
        tor.to_edge(RIGHT, buff=0.8).shift(UP * 0.5)
        hk = time_knife(tor, at=0.58)
        vk = space_knife(tor, bond=6)
        for k in (hk, vk):
            k.glow.set_stroke(opacity=0.3)   # the glowing "cut" state used in the film
        z1 = M(r"Z=\sum_k e^{-\beta E_k}", color=TIME, font_size=40)
        z2 = M(r"Z=\operatorname{Tr}X_\beta^{\,L}", color=SPACE, font_size=40)
        zs = VGroup(z1, z2).arrange(RIGHT, buff=0.7).next_to(tor, DOWN, buff=0.75)

        spin = T(r"spin-1 Heisenberg chain", font_size=30, color=INTEGER)
        spin.next_to(sub, DOWN, aligned_edge=LEFT, buff=0.45)
        self.add(left, spin, tor, hk, vk, zs)
