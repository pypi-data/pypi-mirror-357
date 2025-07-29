from datetime import datetime,time,date,timedelta
from colored import Fore,Style,Back
TDY=datetime.today()
TDY=datetime(TDY.year,TDY.month,TDY.day)
class WaterMilkOrder:
    def colorize(self,count,total_count,msg):
        return f"{Fore.light_cyan}{count}/{Fore.light_yellow}{count+1}{Fore.light_red} of {total_count}{Fore.green_yellow} -> {Fore.dark_goldenrod}{msg}{Style.reset}"

    def nextRxDate(self):
        self.tmro=self.today+timedelta(days=1)
        self.tmroString=self.tmro.strftime('%A').lower()
        if self.dayString not in self.noMilkDays and self.tmroString in self.noMilkDays:
            if not self.frozen:
                return self.today+timedelta(days=2)
            else:
                pass
        else:
            return self.today+timedelta(days=1)

    def nextOrderDate(self):
        rxd=self.nextRxDate()
        if (rxd-self.today) < timedelta(days=1.999):
            if not self.frozen:
                return True
            else:
                pass
        return False

    def __init__(self,noMilkDays=['wednesday','friday','monday'],today=TDY,department="Dairy",frozen=False):
        if frozen:
            self.orderMsg="[FROZEN Flag]Under RND! Do not use YET!!!"
            #print(self.orderMsg)
            #multi day changes need to be made
            #no load days 2, then 1 off, so yeah
            return

        self.noMilkDays=noMilkDays
        orderLang={True:'Yes',False:'No'}
        self.today=today
        self.dayString=today.strftime('%A').lower()
        self.frozen=frozen
        if department.lower() in ['dairy',]:
            self.WaterRx={
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] "Crate Water"/Milk RX\'d Today? ->':orderLang[self.dayString not in self.noMilkDays],
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] Order "Crate Water"/Milk Today? -> ':orderLang[self.nextOrderDate()],
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] Next "Crate Water"/Milk RX Date From Today({self.today.strftime("%m/%d/%Y")}) is -> ':self.nextRxDate().strftime('%A (%m/%d/%Y)'),
            }
        else:
            self.WaterRx={
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] "Load" RX\'d Today? ->':orderLang[self.dayString not in self.noMilkDays],
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] Order "Load" Today? -> ':orderLang[self.nextOrderDate()],
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] Next "Load" RX Date From Today({self.today.strftime("%m/%d/%Y")}) is -> ':self.nextRxDate().strftime('%A (%m/%d/%Y)'),
            }
        self.orderMsg=[]
        ct=len(self.WaterRx)
        for num,k in enumerate(self.WaterRx):
            mp=f"{k} {Fore.magenta}{self.WaterRx[k]}"
            msg=self.colorize(num,ct,mp)
            self.orderMsg.append(msg)
        self.orderMsg='\n'.join(self.orderMsg)
