*** Settings ***
Library    SeleniumLibrary
Library    Process
Library    OperatingSystem
Library    AllureLibrary
Library    RequestsLibrary
Library    JSONLibrary
Library    Collections

*** Keywords ***

# ---------------------------------------------
# ✅ Atomic browser controls
# ---------------------------------------------

QAppuccino.Open Browser To URL
    [Arguments]    ${put_the_url}    ${put_the_browser}
    Open Browser    ${put_the_url}    ${put_the_browser}

QAppuccino.Maximize Browser Window
    Maximize Browser Window

QAppuccino.Go To URL
    [Arguments]    ${put_the_url}
    Go To    ${put_the_url}

QAppuccino.Go Back To Previous Page
    Go Back

# ---------------------------------------------
# ✅ Atomic waits
# ---------------------------------------------

QAppuccino.Wait Until Element Is Visible By Id
    [Arguments]    ${put_the_id_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Page Contains Element    id=${put_the_id_of_element}    ${set_timeout_in_seconds}

QAppuccino.Wait Until Element Is Visible By XPath
    [Arguments]    ${put_the_xpath_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Page Contains Element    xpath=${put_the_xpath_of_element}    ${set_timeout_in_seconds}

QAppuccino.Wait Until Element Contains Text By XPath
    [Arguments]    ${put_the_xpath_of_element}    ${put_your_text_here}    ${set_timeout_in_seconds}=30s
    Wait Until Element Contains    xpath=${put_the_xpath_of_element}    ${put_your_text_here}    ${set_timeout_in_seconds}

QAppuccino.Wait Until Element Is Not Visible By Id
    [Arguments]    ${put_the_id_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Not Visible    id=${put_the_id_of_element}    ${set_timeout_in_seconds}

QAppuccino.Wait Until Element Is Not Visible By XPath
    [Arguments]    ${put_the_xpath_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Not Visible    xpath=${put_the_xpath_of_element}    ${set_timeout_in_seconds}

QAppuccino.Wait Until Page Contains Text
    [Arguments]    ${put_your_text_here}    ${set_timeout_in_seconds}=30s
    Wait Until Page Contains    ${put_your_text_here}    ${set_timeout_in_seconds}

QAppuccino.Wait Until Element Is Interactable by Id
    [Arguments]    ${put_the_id_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Visible    id=${put_the_id_of_element}    ${set_timeout_in_seconds}
    Wait Until Element Is Enabled    id=${put_the_id_of_element}    ${set_timeout_in_seconds}

QAppuccino.Wait Until Element Is Interactable by XPath
    [Arguments]    ${put_the_xpath_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Visible    xpath=${put_the_xpath_of_element}    ${set_timeout_in_seconds}
    Wait Until Element Is Enabled    xpath=${put_the_xpath_of_element}    ${set_timeout_in_seconds}

# ---------------------------------------------
# ✅ Atomic clicks
# ---------------------------------------------

QAppuccino.Click Element By Id
    [Arguments]    ${put_the_id_of_element}
    Click Element    id=${put_the_id_of_element}

QAppuccino.Click Element By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Click Element    xpath=${put_the_xpath_of_element}

QAppuccino.Click Button By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Click Button    xpath=${put_the_xpath_of_element}

QAppuccino.Click Link By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Click Link    xpath=${put_the_xpath_of_element}

QAppuccino.Click Link By Id
    [Arguments]    ${put_the_id_of_element}
    Click Link    id=${put_the_id_of_element}

# ---------------------------------------------
# ✅ Atomic input
# ---------------------------------------------

QAppuccino.Input Text By Id
    [Arguments]    ${put_the_id_of_element}    ${put_your_text_here}
    Input Text    id=${put_the_id_of_element}    ${put_your_text_here}

# ---------------------------------------------
# ✅ Atomic checks
# ---------------------------------------------

QAppuccino.Element Should Be Visible By Id
    [Arguments]    ${put_the_id_of_element}
    Element Should Be Visible    id=${put_the_id_of_element}

QAppuccino.Element Should Be Visible By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Element Should Be Visible    xpath=${put_the_xpath_of_element}

QAppuccino.Alert Should Be Present
    Alert Should Be Present

QAppuccino.Set Focus To Element By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Set Focus To Element    xpath=${put_the_xpath_of_element}

# ---------------------------------------------
# ✅ Atomic Timestamp and Screenshot
# ---------------------------------------------

QAppuccino.Get Current Timestamp
    ${timestamp}=    Evaluate    datetime.datetime.now().strftime("%Y%m%d%H%M%S")    modules=datetime
    RETURN    ${timestamp}

QAppuccino.Capture Screenshot With Timestamp And Attach To Allure
    [Arguments]    ${put_directory_where_to_save_screenshots}
    ${get_current_timestamp}=    QAppuccino.Get Current Timestamp
    ${set_filename}=    Set Variable    ${get_current_timestamp}_screenshot.png
    Capture Page Screenshot    ${put_directory_where_to_save_screenshots}/${set_filename}
    Attach File    ${put_directory_where_to_save_screenshots}/${set_filename}    Screenshot

QAppuccino.Wait For Seconds
    [Arguments]    ${put_seconds}=3s
    Log    ⏳ Waiting for ${put_seconds} ...
    Sleep   ${put_seconds}

# ---------------------------------------------
# ✅ Atomic Self Healing Steps
# ---------------------------------------------

QAppuccino.Self Healing Click Element
    [Arguments]    ${set_primary_locator}    @{list_fallback_locators}
    ${locators}=    Create List    ${set_primary_locator}    @{list_fallback_locators}
    ${clicked}=     Set Variable    False
    FOR    ${locator}    IN    @{locators}
        ${status}=    Run Keyword And Return Status    Element Should Be Visible    ${locator}    3s
        IF    ${status}
            Click Element    ${locator}
            Log    Clicked element using: ${locator}
            ${clicked}=    Set Variable    True
            Exit For Loop
        END
    END
    Run Keyword Unless    ${clicked}    Fail    All locators failed: ${locators}

QAppuccino.Self Healing Input Text
    [Arguments]    ${set_primary_locator}    ${put_your_text_here}    @{list_fallback_locators}
    ${locators}=    Create List    ${set_primary_locator}    @{list_fallback_locators}
    ${inputted}=    Set Variable    False
    FOR    ${locator}    IN    @{locators}
        ${status}=    Run Keyword And Return Status    Element Should Be Visible    ${locator}    3s
        IF    ${status}
            Input Text    ${locator}    ${put_your_text_here}
            Log    Input text using: ${locator}
            ${inputted}=    Set Variable    True
            Exit For Loop
        END
    END
    Run Keyword Unless    ${inputted}    Fail    All locators failed: ${locators}

QAppuccino.Self Healing Wait Until Element Is Visible
    [Arguments]    ${set_primary_locator}    ${set_timeout_in_seconds}=10s    @{list_fallback_locators}
    ${locators}=    Create List    ${set_primary_locator}    @{list_fallback_locators}
    ${found}=       Set Variable    False
    FOR    ${locator}    IN    @{locators}
        ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    ${set_timeout_in_seconds}
        IF    ${status}
            Log    Found element using: ${locator}
            ${found}=    Set Variable    True
            Exit For Loop
        END
    END
    Run Keyword Unless    ${found}    Fail    Element not visible for any locator: ${locators}
