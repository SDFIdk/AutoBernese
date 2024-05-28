from ab.bsw.campaign import (
    build_campaign_menu,
)


def test_build_campaign_menu():
    campaigns = [
        "/path/to/CAMPAIGN54/foo2222",
        "/some/other/path/tmp/foo",
    ]
    expected = """\

! List of Campaigns
! -----------------
CAMPAIGN 2
  "/path/to/CAMPAIGN54/foo2222"
  "/some/other/path/tmp/foo"
  ## widget = uniline; numlines = 30

MSG_CAMPAIGN 1  "Campaign directory"


# BEGIN_PANEL NO_CONDITION #####################################################
# EDIT LIST OF CAMPAIGNS - MENU_CMP                                            #
#                                                                              #
# > Campaign_directory       <                                                 # CAMPAIGN
#                                                                              #
# END_PANEL ####################################################################
"""
    result = build_campaign_menu(campaigns)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_build_campaign_menu_empty():
    campaigns = []
    expected = """\

! List of Campaigns
! -----------------
CAMPAIGN 0
  ## widget = uniline; numlines = 30

MSG_CAMPAIGN 1  "Campaign directory"


# BEGIN_PANEL NO_CONDITION #####################################################
# EDIT LIST OF CAMPAIGNS - MENU_CMP                                            #
#                                                                              #
# > Campaign_directory       <                                                 # CAMPAIGN
#                                                                              #
# END_PANEL ####################################################################
"""
    result = build_campaign_menu(campaigns)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
