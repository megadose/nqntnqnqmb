from nqntmqmqmb import *
import random,argparse,csv
parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="There are different modes: getEmployees to get all employees of a company, getProfileInformations to get all informations on a profile, searchCompany to search a company from the name of the company , searchProfile to search a profile from a name",required=True)
parser.add_argument("--company", help="Url of the company for get all employes (getEmployees)",required=False)
parser.add_argument("--profile", help="Url of the profile for get all informations (getProfileInformations)",required=False)
parser.add_argument("--searchCompany", help="The name of the target company (searchCompany)",required=False)
parser.add_argument("--searchProfile", help="The name of the target (searchProfile)",required=False)
parser.add_argument("--output", help="Name of the csv output file",required=True)
args = parser.parse_args()

with open('./config.json') as config_file:
    config = random.choice(json.load(config_file))

if args.mode == "getEmployees":
    if args.company!=None:
        company=args.company.split("company/")[1].replace("/","")
        result= getAllEmployees(company,config["JSESSIONID"],config["li_at"])
        keys = result[0].keys()
        with open(str(args.output), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for data in result:
                writer.writerow(data)
        print("You can see all employes in : "+str(args.output))
elif args.mode == "getProfileInformations":
    if args.profile!=None:
        profileTarget=args.profile
        try:
            result= getCompanyFromProfile(profileTarget,config["JSESSIONID"],config["li_at"])
            keys = result[0].keys()
            with open("companys_"+str(args.output), 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=keys)
                writer.writeheader()
                for data in result:
                    writer.writerow(data)
            print("You can see all companys found for the target profile in : "+"companys_"+str(args.output))
        except:
            print("Problems with the company of the target profiles")
        try:
            profileTarget=args.profile
            if profileTarget[len(profileTarget)-1]=="/":
                profileTarget=profileTarget[:len(profileTarget)-1]
            result= getContactInformations(profileTarget,config["JSESSIONID"],config["li_at"])
            keys = result.keys()
            with open("informations_"+str(args.output), 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=keys)
                writer.writeheader()
                writer.writerow(result)
            print("You can see the contact informations the target profile in : "+"informations_"+str(args.output))
        except:
            print("Problems with the contact informations of the target profiles")
elif args.mode == "searchCompany":
    if args.searchCompany!=None:
        company=args.searchCompany
        result= getCompanyFromName(company,config["JSESSIONID"],config["li_at"])
        keys = result[0].keys()
        with open(str(args.output), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for data in result:
                writer.writerow(data)
        print("You can see all found companys in : "+str(args.output))
elif args.mode == "searchProfile":
    if args.searchProfile!=None:
        profile=args.searchProfile
        result= getProfileFromName(profile,config["JSESSIONID"],config["li_at"])
        keys = result[0].keys()
        with open(str(args.output), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for data in result:
                writer.writerow(data)
        print("You can see all found profiles in : "+str(args.output))
