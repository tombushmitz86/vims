## VIMS (Voluenteering information system)

### vims provides a backbone system for a voluntary association where voluenteers can "adopt" individuals in need and assign themselves to volunteering days.

#### Models:

* *User/ UserProfile*: A system user.
* Recipient: An individual or group in need.
* Settlement/Street: Geography models for User and Recipient.

* Adoption: An adoption relation between a user and an individual/group in need.
* PackageType: A package designated for a recipient.
* Delivery: Delivery instance where a package is deliverd to a recipient.

* ActivityDay: An voluenteering day where users can register to.
* ActivityDayVolunteer: A activityday <-> volunteer relation.
* ActivityDayDelivery: A activityday <-> delivery relation.
* ActivityType: Type of voluenteering day.

* LogisticsCenter


#### API

root `/api/`

Users
(Most by [Djoser](https://github.com/sunscrapers/djoser))

* POST `login`
* POST `register` Register a new user.
* POST `activate` Activate a registered user from email link.
* POST `password` Change user password
* POST `password/reset` Email the user with password reset link.
* POST `password/reset/confirm` Finish password reset process.
* GET/PATCH `userprofile/<id>` Get or update a userprofile.

Geography

* GET `geo/settlement`
* GET `geo/street`

Recipients

* GET `recipient/` , Params: `tag, settlement_id`

Adoptions

* GET `adoption/` Get all adoption relations.
* GET `adoption/approved` Get all adoption relations who were approved by admin.

* GET `package/` Get all available package to deliver.

* GET `delivery/` Get all registerd deliveries., Params:
    status: filter deliveries by status
    for_adopted_recipients: filter deliveries by recipients who are adopted by a user.

Activities

* GET `activitytype` Get all activity day types (lookups for client).
* GET `activityday` Get all activity days

* GET `activityday-volunteer` Get all activitydays <-> voluenteer relation.
* GET `activityday-volunteer/<id>` Get all activitydays <-> voluenteer relation for a user.
* POST `activityday-volunteer` Create a new activityday <-> volunteer relation.

* GET `activityday-delivery` Get all activityday <-> delivery relations.
* GET `activityday-delivery/<id>` Get all activityday <-> delivery relations for a user.




### Initialize

The project runs on Django 2.0.2 with Postgresql9.6

* Run `make init` from project root.
* activate venv








