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
        if (rxd-self.today) <= timedelta(days=1.999):
            if not self.frozen:
                return True
            else:
                pass
        return False

    def odays(self,offDays=['monday','sunday','wednesday','friday']):
        tdy=self.today
        count=0
        limit=7
        while True:
            count+=1
            name=tdy.strftime("%A").lower()
            if name not in offDays:
                yield name,tdy,tdy.ctime()
            
            tdy=tdy+timedelta(days=1)
            if count >= 7:
                break

    def order_gap(self,offDays=['monday','sunday','wednesday','friday']):
        tdy=self.today
        nextD=[i for i in self.odays(offDays=offDays)][0]
        print(nextD)
        gap=nextD[1]-tdy
        if gap <= timedelta(0):
            nextD=[i for i in self.odays(offDays=offDays)][1]
            tdy=datetime(self.today.year,self.today.month,self.today.day)
            gap=nextD[1]-tdy
            return gap
        else:
            return gap

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
        elif department.lower() in ['frozen',]:
            nxt=self.order_gap(offDays=self.noMilkDays)
            print(nxt,"z")
            NXT=[i for i in self.odays(offDays=self.noMilkDays)][0]
            if nxt <= timedelta(0):
                nextD=[i for i in self.odays(offDays)][1]
                now=datetime.now()
                gap=nextD[1]-self.today
                NXT=nextD
                
            self.WaterRx={
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] RX Frozen Today? ->':orderLang[self.dayString not in self.noMilkDays],
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] Order Frozen? -> ':orderLang[NXT[1] not in self.noMilkDays],
            f'{Fore.light_yellow}[{Fore.orange_red_1}{department}{Fore.light_yellow}] Next "Frozen RX Date From Today({self.today.strftime("%m/%d/%Y")}) is -> ':NXT[1].strftime('%A (%m/%d/%Y)'),

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
