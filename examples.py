from police_stop_and_search_api.police_api import PoliceAPI

def main():
    # Create an api interface object setting destination folder of downloads
    stop_and_search = PoliceAPI(savefolder='downloads')

    # View list of police forces which may be called
    print('All forces:')
    print(stop_and_search.forces)

    # View list of dates which may be called
    print('\nAll dates:')
    print(stop_and_search.dates)

    # Add target months and forces for which downloads will be performed
    # this may be done a number of ways:
    
    # Specify month and force
    stop_and_search.add_job(dates=['2019-10', '2019-07'],
                            forces=['cambridgeshire', 'cheshire'])
    
    # OR Specify specific date over multiple forces
    stop_and_search.add_job(dates=['2019-10'],
                            forces=['cambridgeshire', 'cheshire'])

    # OR Add all available forces for a given list of months
    stop_and_search.add_job(dates=['2019-08', '2019-07'])

    # OR Add a specific force over multiple months
    stop_and_search.add_job(dates=['2019-08', '2019-07'], forces=['cheshire'])

    # Once all jobs have been added begin download process
    stop_and_search.jobs = stop_and_search.jobs[:5]
    print(stop_and_search.jobs)
    
    stop_and_search.download()
    return

if __name__ == '__main__':
    pass
    #main()
