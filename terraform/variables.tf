variable "credentials" {
  description = "My Credentials"
  default     = "./keys/my-creds.json"

}

variable "project" {
  description = "Project"
  default     = "forward-dream-451119-q3"

}

variable "region" {
  description = "Region"
  default     = "europe-north1"

}

variable "location" {
  description = "Project Location"
  default     = "europe-north1"

}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "weather_dataset"

}

variable "gcs_bucket_name" {
  description = "weather_bucket"
  default     = "forward-dream-451119-q3-terra-bucket"

}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDART"

}

