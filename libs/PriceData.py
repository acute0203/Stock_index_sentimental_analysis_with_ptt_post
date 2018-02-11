import pandas_datareader.data as web 

class PriceData():
    
    def __init__(self, start, end, company = "TSM", source = 'google'):
        #fetch data from google 
        self.f = web.DataReader(company, source, start, end) 
        dates = self._change_date_format()
        self.date_per_change = self._calc_date_price_percentage(dates)
        
    def _change_date_format(self):
        #check date format
        dates =[]
        for x in range(len(self.f)): 
            newdate = str(self.f.index[x]) 
            newdate = newdate[0:10] 
            dates.append(newdate) 
        return dates
    
    def _calc_date_price_percentage(self, dates):
        #store date(key) and change percentage(value) into dictonary 
        date_price_percentage={} 
        #change to percentage 
        last_day_index = 0 
        for date in dates: 
            current_day_index = self.f.loc[date]['Close'] 
            current_day_date=date 
            if dates.index(current_day_date)!=0: 
                #change to percentage 
                #if it's the very first day, there's no index to compare so just pass it 
                current_day_change_percentage=(current_day_index-last_day_index)*100 / last_day_index if last_day_index !=0 else 0 
                #put into dictionary 
                date_price_percentage[current_day_date] = current_day_change_percentage 
            last_day_index = current_day_index
        return date_price_percentage
    
    def get_price_data(self):
        return self.date_per_change