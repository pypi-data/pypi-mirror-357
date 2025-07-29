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
    [Arguments]    ${url}    ${browser}
    Open Browser    ${url}    ${browser}

QAppuccino.Maximize Browser Window
    Maximize Browser Window

QAppuccino.Go To URL
    [Arguments]    ${url}
    Go To    ${url}

QAppuccino.Go Back To Previous Page
    Go Back

# ---------------------------------------------
# ✅ Atomic waits
# ---------------------------------------------

QAppuccino.Wait Until Element Is Visible By Id
    [Arguments]    ${element_id}    ${timeout}=10s
    Wait Until Page Contains Element    id=${element_id}    ${timeout}

QAppuccino.Wait Until Element Is Visible By XPath
    [Arguments]    ${xpath}    ${timeout}=10s
    Wait Until Page Contains Element    xpath=${xpath}    ${timeout}

QAppuccino.Wait Until Element Contains Text By XPath
    [Arguments]    ${xpath}    ${text}    ${timeout}=10s
    Wait Until Element Contains    xpath=${xpath}    ${text}    ${timeout}

QAppuccino.Wait Until Element Is Not Visible By Id
    [Arguments]    ${element_id}    ${timeout}=10s
    Wait Until Element Is Not Visible    id=${element_id}    ${timeout}

QAppuccino.Wait Until Element Is Not Visible By XPath
    [Arguments]    ${xpath}    ${timeout}=10s
    Wait Until Element Is Not Visible    xpath=${xpath}    ${timeout}

QAppuccino.Wait Until Page Contains Text
    [Arguments]    ${text}    ${timeout}=10s
    Wait Until Page Contains    ${text}    ${timeout}

# ---------------------------------------------
# ✅ Atomic clicks
# ---------------------------------------------

QAppuccino.Click Element By Id
    [Arguments]    ${element_id}
    Click Element    id=${element_id}

QAppuccino.Click Element By XPath
    [Arguments]    ${xpath}
    Click Element    xpath=${xpath}

QAppuccino.Click Button By XPath
    [Arguments]    ${xpath}
    Click Button    xpath=${xpath}

QAppuccino.Click Link By XPath
    [Arguments]    ${xpath}
    Click Link    xpath=${xpath}

QAppuccino.Click Link By Id
    [Arguments]    ${element_id}
    Click Link    id=${element_id}

# ---------------------------------------------
# ✅ Atomic input
# ---------------------------------------------

QAppuccino.Input Text By Id
    [Arguments]    ${element_id}    ${text}
    Input Text    id=${element_id}    ${text}

# ---------------------------------------------
# ✅ Atomic checks
# ---------------------------------------------

QAppuccino.Element Should Be Visible By Id
    [Arguments]    ${element_id}
    Element Should Be Visible    id=${element_id}

QAppuccino.Element Should Be Visible By XPath
    [Arguments]    ${xpath}
    Element Should Be Visible    xpath=${xpath}

QAppuccino.Alert Should Be Present
    Alert Should Be Present

QAppuccino.Set Focus To Element By XPath
    [Arguments]    ${xpath}
    Set Focus To Element    xpath=${xpath}

# ---------------------------------------------
# ✅ Atomic Timestamp and Screenshot
# ---------------------------------------------

QAppuccino.Get Current Timestamp
    ${timestamp}=    Evaluate    datetime.datetime.now().strftime("%Y%m%d%H%M%S")    modules=datetime
    RETURN    ${timestamp}

QAppuccino.Capture Screenshot With Timestamp And Attach To Allure
    [Arguments]    ${allure_dir}
    ${timestamp}=    QAppuccino.Get Current Timestamp
    ${filename}=    Set Variable    ${timestamp}_screenshot.png
    Capture Page Screenshot    ${allure_dir}/${filename}
    Attach File    ${allure_dir}/${filename}    Screenshot

# ---------------------------------------------
# ✅ Atomic Self Healing Steps
# ---------------------------------------------

QAppuccino.Self Healing Click Element
    [Arguments]    ${primary_locator}    @{fallback_locators}
    ${locators}=    Create List    ${primary_locator}    @{fallback_locators}
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
    [Arguments]    ${primary_locator}    ${text}    @{fallback_locators}
    ${locators}=    Create List    ${primary_locator}    @{fallback_locators}
    ${inputted}=    Set Variable    False
    FOR    ${locator}    IN    @{locators}
        ${status}=    Run Keyword And Return Status    Element Should Be Visible    ${locator}    3s
        IF    ${status}
            Input Text    ${locator}    ${text}
            Log    Input text using: ${locator}
            ${inputted}=    Set Variable    True
            Exit For Loop
        END
    END
    Run Keyword Unless    ${inputted}    Fail    All locators failed: ${locators}

QAppuccino.Self Healing Wait Until Element Is Visible
    [Arguments]    ${primary_locator}    ${timeout}=10s    @{fallback_locators}
    ${locators}=    Create List    ${primary_locator}    @{fallback_locators}
    ${found}=       Set Variable    False
    FOR    ${locator}    IN    @{locators}
        ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    ${timeout}
        IF    ${status}
            Log    Found element using: ${locator}
            ${found}=    Set Variable    True
            Exit For Loop
        END
    END
    Run Keyword Unless    ${found}    Fail    Element not visible for any locator: ${locators}
