async function startProcess() {
    let crm = document.getElementById('crm').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];

    if (!crm || !username || !password || !file) {
        alert("Please fill out all fields and upload a CSV file.");
        return;
    }

    // Implementing the logic to process CRM
    if (crm.includes("https://")) {
        crm = crm.split("https://")[1];
        if (crm.includes("/")) {
            crm = crm.split("/")[0];
        }
    }

    const reader = new FileReader();
    reader.onload = async function(e) {
        const csvContent = e.target.result;
        const advertisers = await parseCSV(csvContent);
        
        const session = new Session(crm, username, password);
        await session.startSession();

        for (const advertiser of advertisers) {
            const response = await advertiser.createAdvertiser(session);
            console.log("Advertiser created:", response);
        }
    };

    reader.readAsText(file);
}

// Your JavaScript classes and functions here

class Advertiser {
    constructor({
        address,
        confirm_password,
        password,
        country,
        description,
        email,
        first_name,
        last_name,
        name,
        phone,
        skype,
        telegram,
        brand_id = null,
        integration_id = null,
        provider_id = null,
        reference = null,
        settings = null,
        status = 1,
        system_role = "0",
        archived = "0"
    }) {
        this.address = address;
        this.confirm_password = confirm_password;
        this.password = password;
        this.country = country;
        this.description = description;
        this.email = email;
        this.first_name = first_name;
        this.last_name = last_name;
        this.name = name;
        this.phone = phone;
        this.skype = skype;
        this.telegram = telegram;
        this.brand_id = brand_id;
        this.integration_id = integration_id;
        this.provider_id = provider_id;
        this.reference = reference;
        this.settings = settings;
        this.status = status;
        this.system_role = system_role;
        this.archived = archived;
    }

    async createAdvertiser(session) {
        const headers = {
            "Authorization": `Bearer ${session.mainToken}`,
            "Content-Type": "application/json",
            "Accept": "application/json"
        };
        const url = `https://${session.crm}/backend/api/v1/crm/action/process`;
        const body = {
            "action": "Advertiser\\Insert",
            "repository": "Eloquent\\AdvertiserRepository",
            "arguments": {
                integration_id: this.integration_id,
                provider_id: this.provider_id,
                name: this.name,
                brand_id: this.brand_id,
                first_name: this.first_name,
                last_name: this.last_name,
                email: this.email,
                system_role: this.system_role,
                reference: this.reference,
                country: this.country,
                address: this.address,
                phone: this.phone,
                skype: this.skype,
                telegram: this.telegram,
                description: this.description,
                status: this.status,
                archived: this.archived,
                password: this.password,
                confirm_password: this.confirm_password,
                settings: this.settings
            }
        };

        const response = await fetch(url, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(body)
        });

        return response.json();
    }
}

class Session {
    constructor(crm, username, password) {
        this.crm = crm;
        this.username = username;
        this.password = password;
    }

    async getLoginToken(token = null) {
        const url = "https://id.irev.com/master/backend/api/wizard/v1/login";
        const body = {
            login: this.username,
            password: this.password,
            token_2fa: token,
            redirect: `https://${this.crm}/pt/auth/signin`
        };

        let response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(body)
        }).then(res => res.json());

        if (response.error?.otp === "telegram") {
            const otpCode = prompt("What is the OTP code?");
            body.token_2fa = otpCode;

            response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(body)
            }).then(res => res.json());
        }

        this.loginToken = response.data.access_token;
        return this.loginToken;
    }

    async startSession() {
        await this.getLoginToken();
        const url = `https://${this.crm}/backend/api/v1/crm/sign/callback`;

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${this.loginToken}`,
                "Content-Type": "application/json"
            }
        }).then(res => res.json());

        this.mainToken = response.data.token;
        return this;
    }
}

async function parseCSV(content) {
    const lines = content.split('\n');
    const headers = lines[0].split(',');
    const advertisers = [];

    for (let i = 1; i < lines.length; i++) {
        const row = lines[i].split(',');
        if (row.length === headers.length) {
            const advertiserData = {};
            for (let j = 0; j < headers.length; j++) {
                advertiserData[headers[j].trim()] = row[j].trim();
            }
            advertisers.push(new Advertiser(advertiserData));
        }
    }

    return advertisers;
}
