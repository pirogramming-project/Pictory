from django.db import models



class Frame(models.Model):
    frame_css = models.TextField("프레임 css")
    # 스티커는 역참조 stickers로 접근.
    
class Sticker(models.Model):
    frame = models.ForeignKey(Frame, models.CASCADE, related_name="stickers")
    sticker_image = models.FilePathField("스티커 이미지")
    coor_x = models.FloatField("x좌표")
    coor_y = models.FloatField("y좌표")
    
