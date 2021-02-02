

####
# install.packages("devtools")
# devtools::install_github("iobis/obistools")
# devtools::install_github("EMODnet/skosxml")
# devtools::install_github("EMODnet/EMODnetBiocheck")
####

library(obistools)
library(EMODnetBiocheck)

check_shark_dwca <- function(data_dir_path, dwca_file_name) {
  dwca_zip_path = paste(data_dir_path, "\\", dwca_file_name, ".zip", sep="")
  event_file = unz(dwca_zip_path, "event.txt")
  occurrence_file = unz(dwca_zip_path, "occurrence.txt")
  emof_file = unz(dwca_zip_path, "extendedmeasurementorfact.txt")
  event = read.csv(event_file, header = TRUE, sep='\t')
  occurrence = read.csv(occurrence_file, header = TRUE, sep='\t')
  emof = read.csv(emof_file, header = TRUE, sep='\t')
  remove(event_file)
  remove(occurrence_file)
  remove(emof_file)
  
  IPTreport <- checkdataset(Event = event, Occurrence = occurrence, eMoF = emof)
  data_summary <- IPTreport$datasummary
  mof_summary <- IPTreport$mofsummary
  event_error_table <- IPTreport$dtb$eventerror_table
  occurrence_error_table <- IPTreport$dtb$occurrenceerror_table
  emof_error_table <-IPTreport$dtb$emoferror_table
  general_issues <- IPTreport$dtb$general_issues
  mof_issues <- IPTreport$dtb$mof_issues
  
  write.table(data_summary, paste(data_dir_path, "\\", dwca_file_name, "_SUMMARY_DATA", '.txt', sep=""), na = "NA", sep='\t')
  write.table(mof_summary, paste(data_dir_path, "\\", dwca_file_name, "_SUMMARY_MOF", '.txt', sep=""), na = "NA", sep='\t')
  write.table(event_error_table, paste(data_dir_path, "\\", dwca_file_name, "_ERRORS_EVENT", '.txt', sep=""), na = "NA", sep='\t')
  write.table(occurrence_error_table, paste(data_dir_path, "\\", dwca_file_name, "_ERRORS_OCCURRENCE", '.txt', sep=""), na = "NA", sep='\t')
  write.table(emof_error_table, paste(data_dir_path, "\\", dwca_file_name, "_ERRORS_EMOF", '.txt', sep=""), na = "NA", sep='\t')
  write.table(general_issues, paste(data_dir_path, "\\", dwca_file_name, "_ISSUES_GENERAL", '.txt', sep=""), na = "NA", sep='\t')
  write.table(mof_issues, paste(data_dir_path, "\\", dwca_file_name, "_ISSUES_MOF", '.txt', sep=""), na = "NA", sep='\t')
}

data_dir_path = "C:\\darwincore\\data"

check_shark_dwca(data_dir_path, "dwca-smhi-bacterioplankton-nat_TEST")

check_shark_dwca(data_dir_path, "dwca-smhi-zoobenthos-nat_TEST")

check_shark_dwca(data_dir_path, "dwca-smhi-phytoplankton-nat_TEST")

check_shark_dwca(data_dir_path, "dwca-smhi-zooplankton-nat_TEST")

