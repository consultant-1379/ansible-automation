#!/usr/bin/python2
# ********************************************************************
# Ericsson ENMaaS               Utility Script
# ********************************************************************
#
# (c) Ericsson ENMaaS 2020 - All rights reserved.
#
# The copyright to the computer program(s) herein is the property of Ericsson
# ENMaaS. The programs may be used and/or copied only with the written
# permission from Ericsson ENMaaS or in accordance with the terms and conditions
# stipulated in the agreement/contract under which the program(s) have been
# supplied.
# ********************************************************************
# Name    : AuditUserDetails
# Purpose : Supporting script for ENM user audit
# Team    : AetosDios
# ********************************************************************

import json
import csv
import sys
import datetime

def get_user_details_json(user_details_enm_path):
    user_details_enm = {}
    with open(user_details_enm_path, 'r') as json_file:
        user_details_enm_list = json.load(json_file)
    for user_details in user_details_enm_list:
        user_details_enm[user_details["username"]] = user_details
    return user_details_enm

def get_user_details_csv(tenancy, user_details_csv_path):
    user_details_csv = {}
    expired_users = []
    with open(user_details_csv_path) as csv_file:
        user_details_csv_list = csv.DictReader(csv_file, delimiter=',')
        for user_details in user_details_csv_list:
            if "@ericsson.com" in user_details["E-mail"]:
                tenancy_list = [user_tenancy.strip().lower() for user_tenancy
                in user_details["ENM_Deployment_Name"].split(';')]
                if "all" in tenancy_list or "all deployments" in tenancy_list or tenancy.lower() in tenancy_list:
                    expiry_date = datetime.datetime.strptime(
                        user_details["ENM_Expiry_Date"],'%m/%d/%Y').date()
                    if expiry_date < datetime.datetime.today().date():
                        expired_users.append(user_details["ENM_Username"].lower())
                    else:
                        user_details_csv[user_details["ENM_Username"].lower()] = user_details
                        user_details_csv[user_details["ENM_Username"].lower()][
                            "privileges"] = [privilege.upper() for privilege in
                            user_details_csv[user_details["ENM_Username"].lower()][
                                "ENM_Access_Right"].split(';')]

    user_details_csv = json.loads(json.dumps(user_details_csv))
    return user_details_csv,expired_users

def get_user_details_with_privileges(user_details_enm_path,
user_privileges_enm_path):
    user_details_enm = get_user_details_json(user_details_enm_path)
    with open(user_privileges_enm_path, 'r') as json_file:
        enm_privileges_list = json.load(json_file)
    for privileges_list in enm_privileges_list:
        for user_privileges in privileges_list:
            user_details_enm[user_privileges["user"]]["privileges"].append(
                user_privileges["role"])
    return user_details_enm

def compare_user_details(user_details_csv, user_details_enm, expired_users):
    csv_users = set(user_details_csv.keys())
    enm_users = set(user_details_enm.keys())
    expired_users = enm_users.intersection(set(expired_users))
    enm_users = enm_users.difference(expired_users)
    missing_enm_users = csv_users.difference(enm_users)
    missing_provided_users = enm_users.difference(csv_users)

    common_users = csv_users.intersection(enm_users)
    privileges_mismatch = {}
    for user in common_users:
        if not sorted(user_details_enm[user]["privileges"]) == sorted(
            user_details_csv[user]["privileges"]):
            privilege_list = {}
            privilege_list["enm_privileges"] = (
                user_details_enm[user]["privileges"])
            privilege_list["csv_privileges"] = (
                user_details_csv[user]["privileges"])
            privileges_mismatch.update({user:privilege_list})
    return list(expired_users), list(missing_enm_users),list(
        missing_provided_users), privileges_mismatch

def main(
    tenancy, user_details_csv_path, user_details_enm_path,
    user_privileges_enm_path):
    user_details_csv,expired_users = get_user_details_csv(
        tenancy,user_details_csv_path)
    user_details_enm = get_user_details_with_privileges(
        user_details_enm_path,user_privileges_enm_path)
    compare_response = compare_user_details(
        user_details_csv, user_details_enm,expired_users)

    user_audit = {}
    user_audit["expired_users"] = compare_response[0]
    user_audit["missing_enm_users"] = compare_response[1]
    user_audit["missing_csv_users"] = compare_response[2]
    user_audit["privilege_mismatch"] = compare_response[3]

    print(json.dumps(user_audit))

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],sys.argv[3], sys.argv[4])
