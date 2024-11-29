


# BHealth - Efficient Laboratory Services Management Application 



BHealth is a web and mobile application designed to streamline laboratory services management in Bosnia and Herzegovina. The application caters to two types of customers: users seeking laboratory services and private laboratories providing those services. BHealth offers a user-friendly platform for searching, comparing, and scheduling appointments for laboratory services, while also providing a secure space for users to store and access their test results. For laboratories, BHealth offers a unique solution to manage their entire workflow, including storing previous and future appointments. 



## Key Features 



Efficient Search and Comparison: Users can easily search and compare laboratory services based on various parameters such as location, price, and service availability. This feature enables users to make informed decisions and choose the most suitable laboratory for their needs. 



Appointment Scheduling: BHealth provides a seamless appointment scheduling system, allowing users to book appointments for laboratory services directly through the application. This feature saves time and eliminates the hassle of making appointments over the phone or in person. 



Secure Test Result Storage: Users can securely store and access their test results within the application. BHealth ensures data privacy and confidentiality, providing a convenient and centralized location for users to keep track of their medical records. 



Streamlined Workflow for Laboratories: Private laboratories benefit from BHealth's comprehensive solution, which centralizes their entire working flow. The application allows laboratories to manage their appointments, store previous records, and plan for future appointments efficiently. 



## Getting Started 



To use BHealth, follow these steps: 



Clone the repository from GitHub, or download the zip file. There are two options to start the code: 



1. Locally, by entering the downloaded/cloned file and providing next commands: 



docker-compose build 

docker-compose up 



Please note that if you are using Windows operating system, you will have to install the Docker application locally, together with needed dependencies. 

If using this version, please use url variable for accessing APIs in Postman/on the server.  Also, this version will not work without starting the RabbitMQ on http://localhost:15672/ being signed in as guest (guest). Therefore, please use the hosted version.



2. The hosted version, by entering: 



ssh root@164.90.216.232 (enter the password written in Appendix) 

docker-compose up 



This version is preffered, since it is faster and easier to access. If using this version, please use live_url variable for accessing APIs in Postman/on the server. 



However, if no insight into the technical background of the backend part is needed, feel free to follow the instructions here github.com/adnasal/bhealth-mvp-frontend in order to access the application.



## Contributions 



We welcome contributions to BHealth! If you find any issues or have ideas for improvements, please submit a pull request. Make sure to follow the guidelines provided in the repository's CONTRIBUTING.md file. 

License 



BHealth is released under the MIT License. You are free to use, modify, and distribute the application in compliance with the license terms. 

Contact 



If you have any questions or feedback regarding BHealth, feel free to reach out to our team at [adnasalkovic@hotmail.com]. We value your input and strive to provide the best possible experience to our users and laboratory partners. 



Thank you for choosing BHealth! We hope the application proves valuable in managing laboratory services efficiently and effectively. 



Best regards, 

The BHealth Team
