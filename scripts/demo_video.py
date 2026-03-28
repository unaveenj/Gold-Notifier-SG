"""
Gold Notifier — Demo Video (Manim Community Edition)

Paste the contents of this file into a Colab cell using %%writefile demo_video.py,
or use the single-cell runner script below.

Single cell runner (paste into one Colab cell and run):
─────────────────────────────────────────────────────────
import subprocess, sys
subprocess.run(["apt-get","install","-y","libpango1.0-dev","libcairo2-dev","pkg-config","python3-dev"], capture_output=True)
subprocess.run([sys.executable,"-m","pip","install","-q","numpy<2.0","manim"], capture_output=True)
# then copy this file content into demo_video.py and run:
# !python -m manim -pql demo_video.py GoldNotifierDemo
─────────────────────────────────────────────────────────
"""

from manim import *

GOLD       = "#c8a84b"
GOLD_LIGHT = "#f5d87a"
DARK_BG    = "#070708"
DARK_CARD  = "#111113"
TEXT_MAIN  = "#e8dfc8"
TEXT_SUB   = "#9a8e78"
GREEN      = "#6fd46f"
RED        = "#e06b6b"


class GoldNotifierDemo(Scene):
    def construct(self):
        self.camera.background_color = DARK_BG
        self.intro()
        self.problem()
        self.solution()
        self.how_it_works()
        self.shops()
        self.email_preview()
        self.outro()

    def intro(self):
        coin = Text("🪙", font_size=72).shift(UP * 0.6)
        title = Text("Gold Notifier", font_size=56, color=GOLD, weight=BOLD)
        tagline = Text("Free Gold Price Alerts · Singapore", font_size=22, color=TEXT_SUB)
        tagline.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(coin, scale=0.5), run_time=0.6)
        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(tagline, shift=UP * 0.2), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(coin), FadeOut(title), FadeOut(tagline))

    def problem(self):
        q = Text("Which jeweller has the\nbest gold price today?",
                 font_size=38, color=TEXT_MAIN, line_spacing=1.3)
        q.set_color_by_text("best gold price", GOLD)
        shops_raw = [("Mustafa",    "S$204.40"),
                     ("Malabar",    "S$206.00"),
                     ("Joyalukkas", "S$205.50"),
                     ("GRT Jewels", "S$203.80")]
        cards = VGroup()
        for name, price in shops_raw:
            card = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.1,
                                    fill_color=DARK_CARD, fill_opacity=1,
                                    stroke_color=GOLD, stroke_width=0.8)
            n = Text(name,  font_size=18, color=TEXT_SUB)
            p = Text(price, font_size=26, color=GOLD, weight=BOLD)
            n.move_to(card).shift(UP * 0.18)
            p.move_to(card).shift(DOWN * 0.18)
            cards.add(VGroup(card, n, p))
        cards.arrange(RIGHT, buff=0.35).shift(DOWN * 0.5)
        q.shift(UP * 2)
        self.play(FadeIn(q, shift=DOWN * 0.3), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.18), run_time=1.2)
        self.wait(1.0)
        highlight = SurroundingRectangle(cards[3], color=GREEN, buff=0.08, stroke_width=2)
        lowest = Text("Lowest today", font_size=16, color=GREEN)
        lowest.next_to(highlight, DOWN, buff=0.15)
        self.play(Create(highlight), FadeIn(lowest), run_time=0.5)
        self.wait(1.2)
        pain = Text("But this changes every few hours...", font_size=22, color=RED)
        pain.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(pain, shift=UP * 0.2))
        self.wait(1.0)
        self.play(FadeOut(VGroup(q, cards, highlight, lowest, pain)))

    def solution(self):
        headline = Text("Gold Notifier monitors all 4 shops\nand emails you automatically.",
                        font_size=34, color=TEXT_MAIN, line_spacing=1.35)
        headline.set_color_by_text("emails you automatically", GOLD)
        perks = VGroup(
            Text("✓  22k & 24k prices", font_size=22, color=TEXT_MAIN),
            Text("✓  Every 2 hours · 8am - 8pm SGT", font_size=22, color=TEXT_MAIN),
            Text("✓  100% free · No app needed", font_size=22, color=TEXT_MAIN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        perks.next_to(headline, DOWN, buff=0.7)
        self.play(FadeIn(headline, shift=UP * 0.3), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.3) for p in perks], lag_ratio=0.25), run_time=1.0)
        self.wait(1.5)
        self.play(FadeOut(VGroup(headline, perks)))

    def how_it_works(self):
        label = Text("HOW IT WORKS", font_size=16, color=GOLD, weight=BOLD).to_edge(UP, buff=0.6)
        steps = [("①", "Subscribe",      "Enter your email at\ngoldnotifier.com"),
                 ("②", "We Monitor",     "Scraper checks 4 jewellers\nevery 2 hours"),
                 ("③", "You Are Alerted","Price email lands in\nyour inbox instantly")]
        cards = VGroup()
        arrows = VGroup()
        for num, title, desc in steps:
            card = RoundedRectangle(corner_radius=0.2, width=3.0, height=2.4,
                                    fill_color=DARK_CARD, fill_opacity=1,
                                    stroke_color=GOLD, stroke_width=0.7)
            n = Text(num,   font_size=30, color=GOLD)
            t = Text(title, font_size=22, color=TEXT_MAIN, weight=BOLD)
            d = Text(desc,  font_size=15, color=TEXT_SUB, line_spacing=1.3)
            n.move_to(card).shift(UP * 0.75)
            t.move_to(card).shift(UP * 0.18)
            d.move_to(card).shift(DOWN * 0.45)
            cards.add(VGroup(card, n, t, d))
        cards.arrange(RIGHT, buff=0.6).shift(DOWN * 0.2)
        for i in range(len(steps) - 1):
            arrows.add(Arrow(cards[i].get_right(), cards[i+1].get_left(),
                             buff=0.1, color=GOLD, stroke_width=2, tip_length=0.18))
        self.play(FadeIn(label, shift=DOWN * 0.2))
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in cards], lag_ratio=0.25), run_time=1.2)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3))
        self.wait(1.5)
        self.play(FadeOut(VGroup(label, cards, arrows)))

    def shops(self):
        label = Text("4 JEWELLERS TRACKED", font_size=16, color=GOLD, weight=BOLD).to_edge(UP, buff=0.6)
        shop_data = [("Mustafa Jewellery", "BeautifulSoup · HTML"),
                     ("Malabar Gold SG",   "BeautifulSoup · HTML"),
                     ("Joyalukkas SG",     "GraphQL API"),
                     ("GRT Jewels SG",     "Cloudscraper")]
        rows = VGroup()
        for name, method in shop_data:
            row = VGroup(Dot(color=GOLD, radius=0.07),
                         Text(name,   font_size=22, color=TEXT_MAIN),
                         Text(method, font_size=16, color=TEXT_SUB)).arrange(RIGHT, buff=0.35)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45).center().shift(DOWN * 0.2)
        self.play(FadeIn(label))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.2), run_time=1.0)
        self.wait(1.5)
        self.play(FadeOut(VGroup(label, rows)))

    def email_preview(self):
        label = Text("WHAT YOU RECEIVE", font_size=16, color=GOLD, weight=BOLD).to_edge(UP, buff=0.6)
        email_bg = RoundedRectangle(corner_radius=0.25, width=8.5, height=4.8,
                                    fill_color=DARK_CARD, fill_opacity=1,
                                    stroke_color=GOLD, stroke_width=0.8).shift(DOWN * 0.15)
        subject = Text("Subject: Gold Prices · 28 Mar 10:05 AM", font_size=16, color=TEXT_SUB)
        subject.move_to(email_bg).shift(UP * 2.0)
        divider = Line(LEFT * 3.8, RIGHT * 3.8, stroke_color=GOLD, stroke_width=0.5, stroke_opacity=0.4)
        divider.move_to(email_bg).shift(UP * 1.65)
        header = Text("Gold Price Update (SGD)", font_size=22, color=GOLD, weight=BOLD)
        header.move_to(email_bg).shift(UP * 1.25)
        lines = [("Mustafa Jewellery", "22k: S$204.40   24k: S$222.00", TEXT_MAIN),
                 ("Malabar Gold SG",   "22k: S$206.00   24k: S$224.50", TEXT_MAIN),
                 ("Joyalukkas SG",     "22k: S$205.50   24k: S$223.80", TEXT_MAIN),
                 ("GRT Jewels SG",     "22k: S$203.80   24k: S$221.60", GREEN)]
        price_group = VGroup()
        for shop, prices, color in lines:
            row = VGroup(Text(shop,   font_size=15, color=TEXT_SUB),
                         Text(prices, font_size=17, color=color, weight=BOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
            price_group.add(row)
        price_group.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        price_group.move_to(email_bg).shift(DOWN * 0.15 + LEFT * 1.2)
        lowest_tag = Text("★ GRT Jewels lowest today", font_size=14, color=GREEN)
        lowest_tag.move_to(email_bg).shift(DOWN * 1.85)
        footer_text = Text("goldnotifier.com  ·  Unsubscribe", font_size=12, color=TEXT_SUB)
        footer_text.move_to(email_bg).shift(DOWN * 2.15)
        self.play(FadeIn(label))
        self.play(FadeIn(email_bg, scale=0.95), run_time=0.5)
        self.play(FadeIn(subject), Create(divider), run_time=0.4)
        self.play(FadeIn(header))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in price_group], lag_ratio=0.15), run_time=1.0)
        self.play(FadeIn(lowest_tag), FadeIn(footer_text))
        self.wait(2.0)
        self.play(FadeOut(VGroup(label, email_bg, subject, divider, header,
                                 price_group, lowest_tag, footer_text)))

    def outro(self):
        coin  = Text("🪙", font_size=64).shift(UP * 1.8)
        title = Text("Gold Notifier", font_size=52, color=GOLD, weight=BOLD)
        url   = Text("goldnotifier.com", font_size=28, color=GOLD_LIGHT)
        free  = Text("Free · No app · Just email", font_size=20, color=TEXT_SUB)
        url.next_to(title, DOWN, buff=0.35)
        free.next_to(url, DOWN, buff=0.25)
        self.play(FadeIn(coin, scale=0.5), run_time=0.5)
        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(url, shift=UP * 0.2), FadeIn(free, shift=UP * 0.2))
        self.wait(2.5)
        self.play(FadeOut(VGroup(coin, title, url, free)))
