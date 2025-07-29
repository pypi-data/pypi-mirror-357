# Dr.Egeria - designing data - part 1
## Introduction

As data professionals, we often need to design data to be collected, processed, and shared with others.
The Egeria Data Designer module has been designed to support this. Using the features of data designer we can
define and refine:

* Data Structures - a composition of data fields (and data structures) that we work with as a unit. For instance, in
a clinical trial, each measurement record we receive will conform to a data structure.
* Data Fields - the building blocks of data structures - for example, in a clinical trial data structure we might find data fields for health measurements, a time and date when the measurements were made and a patient identifier.
* Data Classes - data classes contain a set of rules that describe the allowable values of a kind of data. For instance, when we we receive new data, perhaps we expect a clinical trial measurement record, then we will often want to validate that it conforms to our expectations; that the value of each field, conforms to the data class specification.
Similarly, if we receive some data and aren't sure what it is, we can compare the values we have received with this same set of rules to propose what kind of data it might be.

These are basic building blocks. The following diagram shows how these building blocks come together in a simple example. The ficticious Coco Pharmaceuticals company
is running a drug trial to measure the effectiveness of their experimental treatment of Teddy Bear Drop Foot. Each hospital participating in the trial provides
weekly clinical data records. The clinical trial has established the following data specification to exchange this weekly measurement data.

* A data structure named `TBDF-Incoming Weekly Measurement Data` that is composed of:
* Data Field: Date
* Data Field: PatientId
* Data Field: AngleLeft
* Data Field: AngleRight

* The data field `PatientId` is composed of two sub-fields
* Data Field: HospitalId
* Data Field: PatientNumber

Dr.Egeria allows us to easily sketch this out, and then refine the definitions incrementally as we work through the design.
So lets begin. First we will define the `TBDF-Incoming Weekly Measurement Data` data structure. We will then Don't Create the new data fields.

___


# Update Data Structure

## Data Structure Name 

TBDF-Incoming Weekly Measurement Data

## GUID
fd9380f4-1067-4f7b-bf3f-cb2f3a0e8341

## Qualified Name
DataStruct::TBDF-Incoming Weekly Measurement Data

## Description
This describes the weekly measurement data for each patient for the Teddy Bear drop foot clinical trial.

## Data Fields


## Data Specification


## Namespace


## Version Identifier


## Extended Properties
{}

## Additional Properties
{}


## In Data Dictionary



## In Data Specification




> Note: While not required, it is good practice to end each Dr.Egeria command with a `___` so that a markdown
> seperator is displayed between commands. It improves the readability.

#  Don't Create Data Field
## Data Field
Date
## Description
A date of the form YYYY-MM-DD

___

#  Don't Create Data Field
## Data Field Name
PatientId
## Description
Unique identifier of the patient

___

#  Don't Create Data Field
## Data Field Name
AngleLeft
## Description
Angle rotation of the left leg from vertical

___

#  Don't Create Data Field
## Data Field Name
AngleRight
## Description
Angle rotation of the left leg from vertical

___

#  Don't Create Data Field
## Data Field Name

HospitalId

## Description
Unique identifier for a hospital. Used in forming PatientId.

___

#  Don't Create Data Field
## Data Field Name
PatientNumber
## Description
Unique identifier of the patient within a hospital.

___



# Provenance

* Results from processing file dr_egeria_data_designer_1.md on 2025-06-22 21:06
