import requests
import datetime
from dateutil import parser

#https://xlsxwriter.readthedocs.io/examples.html
import xlsxwriter

# list of Stellar addresses with custom friendly names used for excel tabs naming
addresses = [
    ["GAVPGI..........................................DUYQTMIK", "Address One"],
    ["GAV3Y5..........................................C4MS3NW6", "Address Two"],
    ["GBAN2R..........................................LKVBUH6", "Address Three"]
]

# if we don't want to name tabs with friendly names, we use account values shortened
TabWithFriedlyName = True

# Create a workbook.
workbook = xlsxwriter.Workbook("stellarTransactions_{}.xlsx".format(str(datetime.date.today())),{'strings_to_numbers': True})

# loop through addresses and collect data for each
for address in addresses:
    
    # get friendly name from the array
    friendlyName = address[1]

    # prepare url to query data
    url = "https://horizon.stellar.lobstr.co/accounts/" + address[0] + "/effects?limit=200&order=desc"

    # get JSON response
    response1 = requests.request("GET", url).json()

    # prepare array for storing url for pagination (when there are more than 200 transactions)
    list_of_urls = []

    # append first url where we query data
    list_of_urls.append(url)

    # get number of transactions
    records_count = len(response1['_embedded']['records'])


    # we'll set this to false when we reach end of pages
    pages_remaining = True

    # loop through pages and get the "next" url and append it to the list_of_urls
    while pages_remaining:
        if records_count > 0:
            #print(records_count)
            url = response1['_links']['next']['href']
            response1 = requests.request("GET", url).json()
            records_count = len(response1['_embedded']['records'])
            if records_count != 0:
                list_of_urls.append(url)
            
        else:
            pages_remaining = False


    # declare response array where we'll append data from each url that we gathered in list_of_urls
    response = []

    # loop each url and append returned data (transactions) to response array
    for url in list_of_urls:
        response.append(requests.request("GET", url).json()['_embedded']['records'])


    # declare name that we apply to the tab
    tabName = friendlyName

    # if we don't want to name tabs with friendly names, we use account values shortened
    if not TabWithFriedlyName:
        # get account
        account = response[0][0]['account']

        # get first 4 and last 4 characters
        account_shortened = account[0:4]+"-----"+account[-4:]

        tabName = account_shortened


    # add worksheet with name
    worksheet = workbook.add_worksheet(tabName)
    
    # Column A width set to 15.
    worksheet.set_column('A:A', 15)

    # Add a bold format for the headers.
    bold = workbook.add_format({'bold': 1})

    # Add a number format for cells with money.
    money = workbook.add_format({'num_format': '$#,##0'})

    # Add a number format for cells with small money.
    small_money = workbook.add_format({'num_format': '$#,##0.00'})  

    # Add a number format for cells with number.
    number = workbook.add_format({'num_format': '#,##0.000000'}) 

    dateformat = workbook.add_format({'num_format': 'dd/mm/yy hh:mm'})

    # Header we want to write to the worksheet.
    header = ['Created At',
        'Type',
        'Sell Amount',
        'Sell Currency', 
        'Price', 
        'offer_id',
        'Buy Amount',
        'Buy Currency',
        "Generated: {}".format(str(datetime.datetime.now()))
        ]

    # applying some formatting to the first row
    cell_format = workbook.add_format()
    cell_format.set_text_wrap()
    cell_format.set_bg_color('#EBF1DE')
    cell_format.set_font_color('#4F6228')
    cell_format.set_bold()
    cell_format.set_align('center')
    cell_format.set_align('vcenter')



    # Start from the first cell. Rows and columns are zero indexed.
    col = 0

    # Iterate over the header data and write it out column by column.
    for value in (header):
        worksheet.write(0, col, value, cell_format)
        col += 1

    # Freeze pane on the top row.
    worksheet.freeze_panes(1, 0)


    # starting from the second row to write the data
    row = 1
    for res in response:
        for record in res:
            order_type = ''
            sold_asset_code = ''
            bought_asset_code = ''
            sold_amount = ''
            price = ''
            bought_amount = ''
            offer_id = ''
            element = ''

            #print(record['account'])
                
            col = 0

            if record['type'] == 'trade':
                #new_response.append(record)
                #print(record['sold_asset_type'])

                if record['bought_asset_type'] == 'native':
                    sold_asset_code = record['sold_asset_code']
                    bought_asset_code = 'XLM' #record['bought_asset_code']
                    #order_type = "Sell"
                else:
                    sold_asset_code =  'XLM' #record['sold_asset_code']
                    bought_asset_code = record['bought_asset_code']
                    #order_type = "Buy"

                sold_amount = record['sold_amount']
                bought_amount =  record['bought_amount']
                offer_id =  record['offer_id']
                created_at = record['created_at']
                yourdate = parser.parse(created_at)
                dt = yourdate.replace(tzinfo=None)
                #element = record


            # clean_values = []
                crypto_item = [dt, order_type, sold_amount, sold_asset_code,price, offer_id,bought_amount, bought_asset_code, element]




                # Iterate over the data and write it out row by row.
                for column_value in (crypto_item):
                
                # column_value = column_value.replace('.', ",")

                    if col == 2 or col == 6:
                        #worksheet.writenumber(row, col, column_value)
                        worksheet.write_number(row, col, float(column_value))
                        # print(column_value)
                    elif col == 4:
                        buy_sell_cell_format = workbook.add_format()
                        if record['bought_asset_type'] == 'native':
                            #cell_format.set_bg_color('#CCFFCC')
                            #worksheet.write(1, col, column_value, cell_format)
                            worksheet.write(row, col, '=G'+str(row+1)+'/C'+str(row+1), number)

                            buy_sell_cell_format.set_bg_color('#FFC7CE')
                            buy_sell_cell_format.set_font_color('#9C0006')
                            worksheet.write(row, 1, "Sell", buy_sell_cell_format)
                        else:
                            worksheet.write(row, col, '=C'+str(row+1)+'/G'+str(row+1), number)
                            
                            buy_sell_cell_format.set_bg_color('#C6EFCE')
                            buy_sell_cell_format.set_font_color('#006100')
                            worksheet.write(row, 1, "Buy", buy_sell_cell_format)
                    elif col == 0:
                        worksheet.write(row, col, column_value, dateformat)
                    # elif col == 1:
                    #     if order_type == "Buy":
                    #         cell_format.set_bg_color('#CCFFCC')
                    #     else:
                    #         cell_format.set_bg_color('#CCCCCC')
                    #     worksheet.write(1, col, column_value, cell_format)
                    else:
                        worksheet.write(row, col, column_value)
                    col += 1

                row += 1

    # Apply the autofilter based on the dimensions of the dataframe.
    worksheet.autofilter(0, 0, 0, len(header)-2)



# don't forget to close the workbook at the end
workbook.close()
