import pygame
import os
import random
pygame.font.init() #ekrana leveli yazdırmak için bu modülü ekledim

WIDTH=750
HEIGHT=600
cooldown=30 #yarım saniye 30 a eşitlenicek ve 30 olduğunda atış yapabilcez ve bu şekilde amaç saniyede 2 tane roket atabilme gücümüzün olması
WIN=pygame.display.set_mode((WIDTH,HEIGHT)) #ekran oluşturduk

#ımageları yüklemek
#arka plan
arka_plan=pygame.image.load(os.path.join("assets","background_space.png"))

#Görev gemisi
gorev_gemısı=pygame.image.load(os.path.join("assets","mission_ship.png"))
#Düşman gemisi
kırmızı_dusman_gemısı=pygame.image.load(os.path.join("assets","enemy_ship_red.png"))
yesıl_dusman_gemısı=pygame.image.load(os.path.join("assets","enemy_ship_green.png"))
mavı_dusman_gemısı=pygame.image.load(os.path.join("assets","enemy_ship_blue.png"))
#Oyuncu lazeri
oyuncu_lazer=pygame.image.load(os.path.join("assets","blue_rocket.png"))
#Düşman lazerleri
laser01=pygame.image.load(os.path.join("assets","laser01.png"))
laser02=pygame.image.load(os.path.join("assets","laser02.png"))
laser03=pygame.image.load(os.path.join("assets","laser03.png"))
def carpısma(object1,object2): #oluşturduğumuz masklerin hepsi buraya geliyor burada döndürülen değer çarpa geliyor
    denk_x=object2.x-object1.x
    denk_y=object2.y-object1.y
    return object1.mask.overlap(object2.mask,(denk_x,denk_y))!=None #obje1', obje2 ile kıyaslıyor mask'leri arasında bir temas varmı diye
    #çarpışma yoksa return none değerini döndürücek buda bazı sorunlara yol açabilir diye
#pygame ve diğer oyun motorlarında iki resmin çarpışması algılanmaz normal şartlarda algılanması için mask yada başka bir isimle anılan bir obje çizmemiz gerekiyor
class Lazer():
    def __init__(self,x,y,img):
        self.x=x
        self.y=y
        self.img=img
        self.mask=pygame.mask.from_surface(self.img) #buraya verdiğimiz fotoğrafı baz alarak buraya mask çizicek
    def hareket(self,velocity):
        self.y+=velocity
    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
    def çarp(self,object):
        return carpısma(object,self) #self burada lazerin kendisi object ise kullanılacak nesne olucak
    def sil_ekrandan(self,height):  #lazerlerin ekran dışına çıktığında hafızadan silinmesini ayarlıyoruz böylelikle oyunun daha efektif çalışmasını sağlıyoruz
        return not(self.y<=height and self.y>=0)
class Gemi():
    def __init__(self,x,y,can=100):
        self.x=x
        self.y=y
        self.can=can
        self.gemi_image=None
        self.lazer_img=None
        self.lazerler=[]
        self.sayac=0
    def Sayac(self):
        if self.sayac>=cooldown:
            self.sayac=0
        else:
            self.sayac+=1
    def ateş(self):
        if self.sayac==0:#ancak bu şekilde atış yapılmasına izin veriyoruz
          lazer=Lazer(self.x,self.y,self.lazer_img)
          self.lazerler.append(lazer)

    def lazer_hareketi(self,velocity,object):#biz iki kere lazer hareketini kullanıcaz çünkü bizim lazerlerimizin düşmanı remove etmesini düşmanın lazerlerininde bizim canımızdan %10 götürmesini istiyoruz o yuzden oyuncu gemisinde overlead ediyoruz
        self.Sayac()
        for lazer in self.lazerler: #listenin içinde lazer varsa hareket ettirecek
            lazer.hareket(velocity)
            if lazer.sil_ekrandan(HEIGHT):  # ekran dışına çıktığında lazeri ekrandan sil
                self.lazerler.remove(lazer)
            elif lazer.çarp(object):
                object.can-=10
                self.lazerler.remove(lazer) #çarpan lazeri yok ediyoruz
    def draw(self,window): #window yukarıdaki WIN'İ alıcak
        window.blit(self.gemi_image,(self.x,self.y)) #x ve y kordinatlarını verdik
        for lazer in self.lazerler:
            lazer.draw(window)

    def get_width(self):
        return self.gemi_image.get_width()
    def get_height(self):
        return self.gemi_image.get_height()

class oyuncu_gemi(Gemi):# gemi classının özelliklerini miras olarak alıyoruz
    def __init__(self,x,y,can=100):
        super().__init__(x,y,can) #yukarıdaki classın özelliklerini kullanıcaz
        self.gemi_image=gorev_gemısı
        self.lazer_img=oyuncu_lazer
        self.mask = pygame.mask.from_surface(self.gemi_image)
        self.maxcan=can
    def ateş(self):
        if self.sayac==0:
          lazer=Lazer(self.x+20,self.y,self.lazer_img)
          self.lazerler.append(lazer)
    def lazer_hareketi(self,velocity,objects):#overaide etdik #objects diyoruz çünkü birden fazla düşman gemisi var enemies listesinde
        self.Sayac()
        for lazer in self.lazerler: #listenin içinde lazer varsa hareket ettirecek
            lazer.hareket(velocity)
            if lazer.sil_ekrandan(HEIGHT):  # ekran dışına çıktığında lazeri ekrandan sil
                self.lazerler.remove(lazer)
            else:
                for object in objects:
                    if lazer.çarp(object):
                        objects.remove(object)
                        if lazer in self.lazerler:#benim lazerim lazer listesinin içerisinde varsa silmeye çalış
                          self.lazerler.remove(lazer) #çarpan lazeri yok ediyoruz

    def canbarı(self,window):
        pygame.draw.rect(window,(255,0,0),(self.x,self.y + self.gemi_image.get_height(),
                                          self.gemi_image.get_width(),7))

        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.gemi_image.get_height(),
                                           int(self.gemi_image.get_width()*(self.can/self.maxcan)),7))
    def draw(self, window):  # window yukarıdaki WIN'İ alıcak
        window.blit(self.gemi_image, (self.x, self.y))  # x ve y kordinatlarını verdik
        self.canbarı(window)
        for lazer in self.lazerler:
            lazer.draw(window)
class dusman_gemi(Gemi):
    Color_Map = {  # Bu bir sözlük yapısı key:value 'lerimiz var
        "red": [kırmızı_dusman_gemısı, laser01],
        "green": [yesıl_dusman_gemısı, laser02],
        "blue": [mavı_dusman_gemısı, laser03]
    }
    def __init__(self,x,y,color,can=100):
        super().__init__(x,y,can) #yukarıdaki classın özelliklerini kullanıcaz
        self.gemi_image, self.lazer_img = self.Color_Map[color]
        self.mask = pygame.mask.from_surface(self.gemi_image)

    def hareket(self,velociyt):
        self.y+=velociyt

    def ateş(self):
        if self.sayac==0:
          lazer=Lazer(self.x-2,self.y,self.lazer_img)
          self.lazerler.append(lazer)

def main():
    run=True #buradan oyunun ne zaman açılıp kapanacağını kontrol ediyoruz
    FPS = 60
    enemies=[]
    enemy_velocity=1
    enemy_lenght=0
    lazer_velocity=5
    level=0
    font=pygame.font.SysFont("Algerian",30) #level yazısı
    game_over=pygame.font.SysFont("Algerian",90) #Game over yazısı
    saat = pygame.time.Clock()
    player_velocity=5
    oyuncu=oyuncu_gemi(330,450)
    kaybetmek=False
    kaybetmek_zaman=0 #game over geldiğinde 3 saniyede oyunu kapatıcak

    def draws(): # objelerimizi ekranımıza çizeceğimiz alan burası
        WIN.blit(arka_plan,(0,0)) #arka planı yi çizdiriyoruz x=0 y=0 dan itibaren
        level_font = font.render("LEVEL:{}".format(level), 1, (255, 255, 255))
        WIN.blit(level_font,(615,10))
        oyuncu.draw(WIN)
        for enemy in enemies: # gemileri çiziyoruz
            enemy.draw(WIN)
        if kaybetmek:
            kaybetmek_label=game_over.render("GAME OVER!",1,(200,0,0))
            WIN.blit(kaybetmek_label,(int(WIDTH/2-(kaybetmek_label.get_width()/2)),int(HEIGHT/2-(kaybetmek_label.get_height()/2))))
        pygame.display.update()


    while run:  # run true olduğu oyun devam edicek while döngüsü 1 saniyede 60 defa dönüyor fps değeri ile
        draws()
        saat.tick(FPS)#1 saniyede 60 kare gösterilmesini istiyoruz
        if oyuncu.can<=0:
            kaybetmek=True
            kaybetmek_zaman+=1
            if kaybetmek_zaman>=FPS*3: #3 saniye geçtiğinde oyunu kapatıcaz
                run=False #kodlar çalışmadığı için donmuş gibi gösteriyor
            else:
                continue # continue görünce program üste çıkıcak
        if len(enemies)==0: #bu şekilde bizim enemies listemiz her boşaldığında tekrar düşman gemileri üretilecek
            enemy_velocity+=1
            enemy_lenght+=5
            level+=1
            lazer_velocity+=1 #lazerin hızını arttırıyoruzki lazer ile gemi hızı orantılı olsun
            global cooldown #yukarıdaki cooldown a erişebilecez
            cooldown-=5 #1 saniyedeki mermi atış hızımı arttıracak
            for i in range(enemy_lenght): #yani enemy_lenght kaçsa o kadar gemi üreticez
                enemy = dusman_gemi(random.randrange(1,700),random.randrange(-1500,-100),
                                    random.choice(["red","green","blue"]))
                enemies.append(enemy) #oluşan gemiyi direk bu enemies listesine gönderiyoruz

        for event in pygame.event.get(): # burada run sürekli true döndüğü için sonsuz döngü oluyor ve program hata veriyor bunu önlemek için
            if event.type==pygame.QUIT:
                run=False

        keys=pygame.key.get_pressed() # tuş takımlarını keys değişkenine atıyoruz
        if keys[pygame.K_LEFT] and oyuncu.x>0: #burada geminin ekranın dışına çıkmamasını sağlıyoruz
            oyuncu.x-=player_velocity
        if keys[pygame.K_RIGHT] and oyuncu.x<670:
            oyuncu.x += player_velocity
        if keys[pygame.K_UP] and oyuncu.y>0:
            oyuncu.y -= player_velocity
        if keys[pygame.K_DOWN] and oyuncu.y<479:
            oyuncu.y += player_velocity
        if keys[pygame.K_SPACE]:
            oyuncu.ateş()

        for enemy in enemies:
            enemy.hareket(enemy_velocity)
            enemy.lazer_hareketi(lazer_velocity,oyuncu)
            if random.randrange(0,2*60)==1: #120'yi azaltırsak daha çok ateş gelicektir
                enemy.ateş()
            if carpısma(enemy,oyuncu):
                oyuncu.can-=10
                enemies.remove(enemy)
            if enemy.y>HEIGHT: #gemiler ekrandan çıktıktan sonra bunları silmemizi sağlıyor hafıza için iyidir
             enemies.remove(enemy)

        oyuncu.lazer_hareketi(-lazer_velocity,enemies)

def main_menü():
    title_font=pygame.font.SysFont("Algerian",50)
    run=True
    while run:
        WIN.blit(arka_plan,(0,0)) #arka planı çiziyoruz1
        main_text=title_font.render("BASLAMAK ICIN FAREYE BASIN",1,(255,255,255)) # 1 burada netlik ayarı
        WIN.blit(main_text,(int(WIDTH/2-main_text.get_width()/2),int(HEIGHT/2-main_text.get_height()/2+45)))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

main_menü()
