*** Settings ***
Library           Keywords.py

*** Test Cases ***
ServiceActivation
    [Setup]    connect_to_db
    ${client}  get_active_client
    should not be equal as numbers  ${client.client_id}   0
    ${current_client_services}     get_services     ${client.client_id}
    ${all_services}     get_services
    ${random_service_off}   get_random_off_service      ${all_services}     ${current_client_services}
    ${ans}  activate_new_service_and_check_it   ${client.client_id}    ${random_service_off[0]}
    should be true  ${ans}
    ${ans}      check_balance   ${client}   ${random_service_off[1]}
    should be true  ${ans}