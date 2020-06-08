import csv  


fields = ['ID',	'Manufacturer',	'Model', 'Category', 'Mileage',	'Gear box type', 'Doors', 'Wheel', 'Color', 'Interior color', 'VIN', 'Leather interior', 'Price', 'Customs']
with open('myauto data.csv', 'w') as csvfile:  
    # creating a csv dict writer object  
    writer = csv.DictWriter(csvfile, fieldnames = fields)  
    # writing headers (field names)  
    writer.writeheader()  
        
