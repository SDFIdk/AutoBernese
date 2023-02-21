workspace "GNSS processing with AutoBernese" {

    model "AutoBernese" {

        external_data_sources = softwareSystem "External data sources"

        enterprise "Agency for Data Supply and Infrastructure" {
            user = person "Geodesist"
            # cron = person "System user | CRON job"

            auto_bernese = softwareSystem "AutoBernese" {
                cli = container "CLI application" {}
                download_api = container "Download API" {
                    downloader = component "Downloader" "Downloads specified files from external data sources." "FTP/HTTP"
                    download_controller = component "Download controller" "Specifies source files and local destinations."
                }
                sitelog_to_sta = container "Sitelog to station file" {
                    gensta = component "Legacy converter" "Converts sitelog to station file." "Perl"
                    gensta_runner = component "gensta runner" "Creates subprocess with a call to the Perl program"
                }
                qaqc = container "Kvalitetssikring [QA] og kvalitetskontrol [QC]" {}
                organiser = container "Input organiser" {}
                bsw_api = container "BSW API" {
                    bpe_interface = component "BPE interface" "Perl scripts that call the Bernese Processing Engine" "Perl 5"
                    bpe_runner = component "BPE runner" "Creates subprocess with a call to the BPE interface"
                }
                fire_api = container "FIRE API" {
                    fire_wrapper = component "FIRE wrapper" "Creates a subprocess that runs FIRE command to read in specified results from the campaign." "MambaForge, FIRE"
                }
            }

            file_server = softwareSystem "File server" {
                datapool = container "BSW DATAPOOL" "The directory BSW uses as common raw-data storage."
                campaign = container "BSW CAMPAIGN" "The directory BSW uses for each campaign area."
                savedisk = container "BSW SAVEDISK" "The directory BSW uses as end-product storage."
                everything_else = container "Everything else" "The rest of the file system used for GNSS-related data."
            }
            bsw = softwareSystem "BSW" {
                bsw_perl_interface = container "BSW Perl modules" "Perl programs that can be used to start the Bernese Processning Engine."
            }
            fire = softwareSystem "FIRE" {}
        }

        # Relationships between people and software systems
        download_api -> external_data_sources "Get data"

        user -> cli "Create campaign, activate campaign"
        user -> cli "Get data from external sources"
        user -> cli "Create STA file from updated sitelog"
        user -> cli "Run PCF file for campaign"
        user -> cli "Export end products"
        user -> cli "Upload results to FIRE Dataase"
        user -> file_server "Get and move end products to own PC"

        cli -> download_api "Get data from sources in campaign.yaml"
        cli -> sitelog_to_sta "Produce/update STA file from sitelog."

        cli -> qaqc "Check data integrity, accessibility, etc."
        cli -> qaqc "Perform quality assurance/control on end products"

        cli -> organiser "Rebuild general input data" ""
        cli -> organiser "Transfer relevant input data to the campaign directory"

        cli -> bsw_api "Create new campaign of given type" "NKG, 5D, KDI, RTK service"
        cli -> bsw_api "Start BPE using campaign-specific PCF file"

        cli -> fire_api "Upload results to FIRE Database" ".CRD and .VEL files"

        # Relationships to/from containers
        download_api -> file_server "Store external data locally"
        bsw_api -> file_server "Store workspace and end products"
        qaqc -> file_server "Assure quality of end products."
        bsw_api -> bsw "Organise campaign and run BPE"
        fire_api -> fire "Upload end products to FIRE database"

        # Relationships to/from components
        # TBW
        # Here will come the interactions between the different parts on the component level.
        gensta_runner -> gensta "Run converter for a given sitelog."
    }

    views {
        # systemlandscape "SystemLandscape" {
        #     include *
        #     animation {
        #         file_server
        #     }
        #     autoLayout
        # }

        systemContext auto_bernese {
            include *
            autolayout lr
        }

        container auto_bernese {
            include *
            autolayout tb
        }

        component download_api "Data" {
            include *
            autoLayout
        }

        component sitelog_to_sta "Sitelog" {
            include *
            autoLayout
        }

        component bsw_api "BSW" {
            include *
            autoLayout
        }

        theme default
    }

}
