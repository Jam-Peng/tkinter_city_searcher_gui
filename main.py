import tkinter as tk
from datetime import datetime, timedelta
import requests
import time
from PIL import Image, ImageTk
from geopy.geocoders import Nominatim, Photon    # 把 Nominatim 換成使用 Photon
from timezonefinder import TimezoneFinder
import pytz
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY')


class App(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.geometry('400x600+300+300')
        self.parent.resizable(False, False)
        self.parent.title('亞洲城市天氣查詢器')
        self.parent.configure(bg='#e9e7df')

        self.count = 0
        self.pages = []
        self.toggle_bar_fm, self.toggle_btn = None, None
        self.next_btn, self.back_btn = None, None
        self.all_dates = []

        # city
        self.option_list = ['台灣/台北(Taipei)', '中國/上海(Shanghai)', '日本/東京(Tokyo)', '韓國/首爾(Seoul)', '香港(Hong Kong)',
                            '澳門(Macau)', '新加坡(Singapore)', '泰國/曼谷(Bangkok)', '馬來西亞/吉隆坡(kuala Lumpur)', '馬尼拉(Manila)',
                            '緬甸/仰光(Yangon)']
        self.city = tk.StringVar()
        self.city.set('台灣(Taipei)')

        # main
        self.main_frame = tk.Frame(self.parent, bg='#51A8DD')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # top slidebar frame
        self.bar_frame = tk.Frame(
            self.main_frame, bg='#e9e7df', highlightbackground='white', highlightthickness=1)
        self.bar_frame.pack(side=tk.TOP, fill=tk.X)
        self.bar_frame.pack_propagate(False)
        self.bar_frame.config(height=50)

        # top slider content
        toggle_btn_font = ('Arial 20 bold')
        self.title_lb = tk.Label(self.bar_frame, text='National Selector',
                                 background='#e9e7df', fg='#454040', font=toggle_btn_font,)
        self.title_lb.pack(side=tk.LEFT, padx=14)

        self.toggle_btn = tk.Button(self.bar_frame, text='≡', bg='#e9e7df', fg='black', font=('Bold', 18), width=1,
                                    bd=0, highlightbackground='#e9e7df', activebackground='#e9e7df', activeforeground='#454040',
                                    command=self.toggle_bar)
        self.toggle_btn.pack(side=tk.RIGHT, padx=5)

        # bottom pageration
        page_btn_font = ('Arial 14 bold')

        self.bottom_frame = tk.Frame(
            self.parent, width=400, height=50, bg='#e9e7df')
        self.bottom_frame.pack(side=tk.BOTTOM, pady=10)

        self.back_btn = tk.Button(self.bottom_frame, text='Back', font=page_btn_font, bg='#e9e7df', fg='black', width=8,
                                  border=0, highlightbackground='#e9e7df', highlightcolor='black', activeforeground='#454040',
                                  command=self.back_page, state=tk.DISABLED)
        self.back_btn.pack(side=tk.LEFT, padx=40)

        self.next_btn = tk.Button(self.bottom_frame, text='Next', font=page_btn_font, bg='#e9e7df', fg='black', width=8,
                                  border=0, highlightbackground='#e9e7df', highlightcolor='black', activeforeground='#454040',
                                  command=self.next_page)
        self.next_btn.pack(side=tk.RIGHT, padx=40)

        # pages
        self.page_1 = Pages(self.main_frame)
        self.page_1.page.pack()
        self.page_2 = Pages(self.main_frame)
        self.page_3 = Pages(self.main_frame)
        self.page_4 = Pages(self.main_frame)
        self.page_5 = Pages(self.main_frame)
        self.page_6 = Pages(self.main_frame)
        self.page_7 = Pages(self.main_frame)
        self.pages = [self.page_1, self.page_2, self.page_3,
                      self.page_4, self.page_5, self.page_6, self.page_7]

    # Get API Data

    def get_city_data(self):
        search_city = self.city.get().split('(')[1][:-1]

        # Closed toggle frame
        if self.toggle_btn.cget('text') != '≡':
            self.toggle_bar_fm.destroy()
            self.toggle_btn.config(text='≡')
            self.toggle_btn.config(command=self.toggle_bar)

        # Search city location
        # geolocator = Nominatim(user_agent='geoapiExercises')  把 Nominatim 換成使用 Photon方法 不然會無法連線地理位置 403
        geolocator = Photon(user_agent='geoapiExercises')
        location = geolocator.geocode(search_city)
        obj = TimezoneFinder()

        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)

        # Current zone time
        home = pytz.timezone(result)
        local_time = datetime.now(home)
        current_time = local_time.strftime('%I:%M %p')

        # Weeks
        date1 = datetime.now()
        date2 = date1+timedelta(days=1)
        date3 = date1+timedelta(days=2)
        date4 = date1+timedelta(days=3)
        date5 = date1+timedelta(days=4)
        date6 = date1+timedelta(days=5)
        date7 = date1+timedelta(days=6)
        self.all_dates = [date1, date2, date3, date4, date5, date6, date7]

        # Zone/City、Long/Lats、clock、weeks
        for p in range(len(self.pages)):
            self.pages[p].timezone.config(text=result)
            self.pages[p].long_lat.config(
                text=f'{round(location.latitude,4)}˚N {round(location.longitude,4)}˚E')
            self.pages[p].clock.config(text=current_time)
            self.pages[p].week.config(text=self.all_dates[p].strftime('%A'))

        # weather API
        api = f"https://api.openweathermap.org/data/2.5/onecall?lat={str(location.latitude)}&lon={str(location.longitude)}&\
            units=metric&exclude=hourly&appid={api_key}"

        json_data = requests.get(api).json()

        # Current day weather
        temp_p1 = int(json_data['current']['temp']-273.15)
        humidity_p1 = json_data['current']['humidity']
        pressure_p1 = json_data['current']['pressure']
        wind_p1 = json_data['current']['wind_speed']
        uv_p1 = int(json_data['current']['uvi'])
        description_p1 = json_data['daily'][0]['weather'][0]['description']
        sunrise_stamp_p1 = json_data['current']['sunrise']
        sunset_stamp_p1 = json_data['current']['sunset']

        self.page_1.t.config(text=f'{temp_p1}˚C')

        day1_icon = json_data['daily'][0]['weather'][0]['icon']
        photo1 = ImageTk.PhotoImage(file=f"icon/{day1_icon}@2x.png")
        self.page_1.weather_icon.config(image=photo1)
        self.page_1.weather_icon.image = photo1

        self.page_1.desc.config(text=description_p1)

        temp_day_p1 = json_data['daily'][0]['temp']['day']-273.15
        temp_night_p1 = json_data['daily'][0]['temp']['night']-273.15
        self.page_1.dayNigth_t.config(
            text=f'Day: {temp_day_p1:.1f}˚  Night: {temp_night_p1:.1f}˚')

        sunrise_p1 = self.stamp_todate(sunrise_stamp_p1)
        self.page_1.sunrise_info.config(text=sunrise_p1)

        sunset_p1 = self.stamp_todate(sunset_stamp_p1)
        self.page_1.sunset_info.config(text=sunset_p1)

        self.page_1.humidity_info.config(text=(humidity_p1, '%'))
        self.page_1.wind_info.config(text=(wind_p1, 'm/s'))
        self.page_1.uvi_info.config(text=uv_p1)
        self.page_1.pressure_info.config(text=(pressure_p1, 'hpa'))

        # Second ~ Seventh days weather
        for i in range(len(self.pages[1:])):
            temp = int(json_data['daily'][i+1]['temp']['day']-273.15)
            humidity = json_data['daily'][i+1]['humidity']
            pressure = json_data['daily'][i+1]['pressure']
            wind = json_data['daily'][i+1]['wind_speed']
            uv = int(json_data['daily'][i+1]['uvi'])
            description = json_data['daily'][i+1]['weather'][0]['description']
            sunrise_stamp = json_data['daily'][i+1]['sunrise']
            sunset_stamp = json_data['daily'][i+1]['sunset']

            self.pages[i+1].t.config(text=f'{temp}˚C')

            day_icon = json_data['daily'][i+1]['weather'][0]['icon']
            photo = ImageTk.PhotoImage(file=f"icon/{day_icon}@2x.png")
            self.pages[i+1].weather_icon.config(image=photo)
            self.pages[i+1].weather_icon.image = photo

            self.pages[i+1].desc.config(text=description)

            temp_day = json_data['daily'][i+1]['temp']['day']-273.15
            temp_night = json_data['daily'][i+1]['temp']['night']-273.15
            self.pages[i+1].dayNigth_t.config(
                text=f'Day: {temp_day:.1f}˚  Night: {temp_night:.1f}˚')

            sunrise = self.stamp_todate(sunrise_stamp)
            self.pages[i+1].sunrise_info.config(text=sunrise)

            sunset = self.stamp_todate(sunset_stamp)
            self.pages[i+1].sunset_info.config(text=sunset)

            self.pages[i+1].humidity_info.config(text=(humidity, '%'))
            self.pages[i+1].wind_info.config(text=(wind, 'm/s'))
            self.pages[i+1].uvi_info.config(text=uv)
            self.pages[i+1].pressure_info.config(text=(pressure, 'hpa'))

    def stamp_todate(self, date_stamp):
        try:
            self.struct_time = time.localtime(date_stamp)
            return time.strftime("%H:%M %p", self.struct_time)
        except Exception as e:
            print(e)
        return None

    def next_page(self):
        if self.toggle_btn.cget('text') != '≡' and not self.count > len(self.pages)-2:
            for i in range(57, -2, -2):
                self.toggle_bar_fm.place(x=0, y=50, width=400, height=i)
                self.parent.update()
                time.sleep(0.006)

            self.toggle_bar_fm.destroy()
            self.toggle_btn.config(text='≡')
            self.toggle_btn.config(command=self.toggle_bar)

            for p in self.pages:
                p.page.pack_forget()

            self.count += 1
            page_frame = self.pages[self.count]
            page_frame.page.pack()
            if self.pages[self.count] == self.page_7:
                self.next_btn.config(state=tk.DISABLED)
            elif self.count != 0:
                self.back_btn.config(state=tk.NORMAL)

        elif not self.count > len(self.pages)-2:
            for p in self.pages:
                p.page.pack_forget()

            self.count += 1
            page_frame = self.pages[self.count]
            page_frame.page.pack()

            if self.pages[self.count] == self.page_7:
                self.next_btn.config(state=tk.DISABLED)
            elif self.count != 0:
                self.back_btn.config(state=tk.NORMAL)

    def back_page(self):
        if self.toggle_btn.cget('text') != '≡' and not self.count == 0:
            for i in range(57, -2, -2):
                self.toggle_bar_fm.place(x=0, y=50, width=400, height=i)
                self.parent.update()
                time.sleep(0.006)

            self.toggle_bar_fm.destroy()
            self.toggle_btn.config(text='≡')
            self.toggle_btn.config(command=self.toggle_bar)

            for p in self.pages:
                p.page.pack_forget()

            page_frame = self.pages[self.count]
            page_frame.page.pack()

        if not self.count == 0:
            for p in self.pages:
                p.page.pack_forget()

            self.count -= 1
            page_frame = self.pages[self.count]
            page_frame.page.pack()

            if self.pages[self.count] == self.page_6:
                self.next_btn.config(state=tk.NORMAL)
            elif self.count == 0:
                self.back_btn.config(state=tk.DISABLED)

    def toggle_bar(self):
        def collapse_toggle_bar():
            for i in range(57, -2, -2):
                self.toggle_bar_fm.place(x=0, y=50, width=400, height=i)
                self.parent.update()
                time.sleep(0.006)

            self.toggle_bar_fm.destroy()
            self.toggle_btn.config(text='≡')
            self.toggle_btn.config(command=self.toggle_bar)

        # toggle frame
        self.toggle_bar_fm = tk.Frame(self.main_frame, bg='#454040')
        for i in range(-1, 57, 2):
            self.toggle_bar_fm.place(x=0, y=50, width=400, height=i)
            self.parent.update()
            time.sleep(0.006)

        # OptionMenu and button widgets
        self.selector = tk.OptionMenu(
            self.toggle_bar_fm, self.city, *self.option_list)
        self.selector.config(width=23, fg='#111111',
                             bg='#454040', font=('Arial', 15), border=0)
        self.selector.pack(side=tk.LEFT, padx=47)

        self.search_btn = tk.Button(self.toggle_bar_fm, text='🔍', font=('Bold', 12), bd=0, fg='black', width=1,
                                    highlightbackground='#454040', activebackground='#454040', activeforeground='#454040',
                                    command=self.get_city_data)
        self.search_btn.pack(side=tk.RIGHT, padx=8)

        self.toggle_btn.config(text='x')
        self.toggle_btn.config(command=collapse_toggle_bar)


class Pages(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.page = tk.Frame(self.parent, width=400, height=510, bg='#51A8DD')

        timezone_font = ('Arial 18')
        long_font = ('Arial', 14)
        clock_font = ('Arial', 30, 'bold')
        week_font = ('Arial', 22, 'bold')
        temp_font = ('Arial', 60, 'bold')
        info_text = ('Arial', 18)
        day_night_font = ('Arial', 14)
        other_info_title = ('Arial', 14)
        other_info_text = ('Arial', 16)

        self.timezone = tk.Label(
            self.page, font=timezone_font, fg='white', bg='#51A8DD')
        self.timezone.place(relx=0.04, y=7)
        self.long_lat = tk.Label(self.page, font=long_font,
                                 fg='white', bg='#51A8DD')
        self.long_lat.place(relx=0.04, y=34)
        self.clock = tk.Label(self.page, font=clock_font,
                              fg='white', bg='#51A8DD')
        self.clock.place(x=250, y=7)
        self.week = tk.Label(self.page, text='Monday',
                             font=week_font, fg='white', bg='#51A8DD')
        self.week.place(relx=0.5, y=88, anchor=tk.CENTER)
        self.t = tk.Label(self.page, text='20˚C', font=temp_font,
                          fg='white', bg='#51A8DD')
        self.t.place(relx=0.5, y=141, anchor=tk.CENTER)
        self.weather_icon = tk.Label(self.page, bg='#51A8DD')
        self.weather_icon.place(relx=0.5, y=217, anchor=tk.CENTER)
        self.desc = tk.Label(self.page, text='Description',
                             font=info_text, fg='white', bg='#51A8DD')
        self.desc.place(relx=0.5, y=257, anchor=tk.CENTER)
        self.dayNigth_t = tk.Label(
            self.page, font=day_night_font, fg='white', bg='#51A8DD')
        self.dayNigth_t.place(relx=0.5, y=280, anchor=tk.CENTER)

        # other weather infos
        self.bg_box = tk.PhotoImage(file='template/frame_bg.png')
        tk.Label(self.page, image=self.bg_box, bg='#51A8DD').place(
            relx=0.5, y=400, anchor=tk.CENTER)

        other_info_frame = tk.Frame(
            self.page, width=340, height=180, bg='#303030')
        other_info_frame.place(relx=0.5, y=400, anchor=tk.CENTER)

        self.sunrise_icon_path = 'template/sunrise.png'
        self.sunrise_img = self.get_img(self.sunrise_icon_path)
        tk.Label(other_info_frame, image=self.sunrise_img,
                 bg='#303030').place(relx=0.18, y=25, anchor=tk.CENTER)

        self.sunrise_title = tk.Label(
            other_info_frame, text='Sunrise', font=other_info_title, fg='white', bg='#303030')
        self.sunrise_title.place(relx=0.18, y=55, anchor=tk.CENTER)
        self.sunrise_info = tk.Label(
            other_info_frame, text='05:25 AM', font=other_info_text, fg='white', bg='#303030')
        self.sunrise_info.place(relx=0.18, y=75, anchor=tk.CENTER)

        self.sunset_icon_path = 'template/sunset.png'
        self.sunset_img = self.get_img(self.sunset_icon_path)
        tk.Label(other_info_frame, image=self.sunset_img, bg='#303030').place(
            relx=0.18, y=115, anchor=tk.CENTER)

        self.sunset_title = tk.Label(
            other_info_frame, text='Sunset', font=other_info_title, fg='white', bg='#303030')
        self.sunset_title.place(relx=0.18, y=145, anchor=tk.CENTER)
        self.sunset_info = tk.Label(
            other_info_frame, text='05:25 AM', font=other_info_text, fg='white', bg='#303030')
        self.sunset_info.place(relx=0.18, y=165, anchor=tk.CENTER)

        self.humidity_icon_path = 'template/humidity.png'
        self.humidity_img = self.get_img(self.humidity_icon_path)
        tk.Label(other_info_frame, image=self.humidity_img,
                 bg='#303030').place(relx=0.5, y=25, anchor=tk.CENTER)

        self.humidity_title = tk.Label(
            other_info_frame, text='Humidity', font=other_info_title, fg='white', bg='#303030')
        self.humidity_title.place(relx=0.5, y=55, anchor=tk.CENTER)
        self.humidity_info = tk.Label(
            other_info_frame, text='66 %', font=other_info_text, fg='white', bg='#303030')
        self.humidity_info.place(relx=0.5, y=75, anchor=tk.CENTER)

        self.wind_icon_path = 'template/wind.png'
        self.wind_img = self.get_img(self.wind_icon_path)
        tk.Label(other_info_frame, image=self.wind_img, bg='#303030').place(
            relx=0.5, y=115, anchor=tk.CENTER)

        self.wind_title = tk.Label(other_info_frame, text='Wind Speed',
                                   font=other_info_title, fg='white', bg='#303030')
        self.wind_title.place(relx=0.5, y=145, anchor=tk.CENTER)
        self.wind_info = tk.Label(
            other_info_frame, text='4 m/s', font=other_info_text, fg='white', bg='#303030')
        self.wind_info.place(relx=0.5, y=165, anchor=tk.CENTER)

        self.uvi_icon_path = 'template/uvi.png'
        self.uvi_img = self.get_img(self.uvi_icon_path)
        tk.Label(other_info_frame, image=self.uvi_img, bg='#303030').place(
            relx=0.82, y=25, anchor=tk.CENTER)

        self.uvi_title = tk.Label(other_info_frame, text='UV',
                                  font=other_info_title, fg='white', bg='#303030')
        self.uvi_title.place(relx=0.82, y=55, anchor=tk.CENTER)
        self.uvi_info = tk.Label(other_info_frame, text='11',
                                 font=other_info_text, fg='white', bg='#303030')
        self.uvi_info.place(relx=0.82, y=75, anchor=tk.CENTER)

        self.pressure_icon_path = 'template/pressure.png'
        self.pressure_img = self.get_img(self.pressure_icon_path)
        tk.Label(other_info_frame, image=self.pressure_img,
                 bg='#303030').place(relx=0.82, y=115, anchor=tk.CENTER)

        self.pressure_title = tk.Label(
            other_info_frame, text='pressure', font=other_info_title, fg='white', bg='#303030')
        self.pressure_title.place(relx=0.82, y=145, anchor=tk.CENTER)
        self.pressure_info = tk.Label(
            other_info_frame, text='1014 hPa', font=other_info_text, fg='white', bg='#303030')
        self.pressure_info.place(relx=0.82, y=165, anchor=tk.CENTER)

    # Resize icon
    def get_img(self, path):
        photo = Image.open(path)
        w, h = photo.width, photo.height
        img = photo.resize((int(w*0.04), int(h*0.04)))
        tk_img = ImageTk.PhotoImage(img)
        return tk_img


win = tk.Tk()
app = App(win).get_city_data()
win.mainloop()
