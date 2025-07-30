import requests
import json
import os


class ReportsApi:
    def __init__(self, base_url: str, token_file: str):
        self.base_url = base_url.rstrip("/")
        self.token = self._load_token(token_file)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

    def _load_token(self, token_file: str) -> str:
        """
        Load bearer token from a JSON file with structure: { "id_token": "<token>" }
        """
        if not os.path.exists(token_file):
            raise FileNotFoundError(f"Token file '{token_file}' not found")

        with open(token_file, 'r') as f:
            data = json.load(f)

        token = data.get("id_token")
        if not token:
            raise ValueError("Missing 'id_token' field in token JSON file")
        return token
    
    def query_sites(self):
        """
        Query the /slices endpoint with optional filters.
        """
        url = f"{self.base_url}/sites"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch slices: {response.status_code} - {response.text}")    

    def query_slices(self, start_time: str = None, end_time: str = None, user_id: list[str] = None,
                     user_email: list[str] = None, project_id: list[str] = None, slice_id: list[str] = None,
                     slice_state: list[str] = None, sliver_id: list[str] = None, sliver_type: list[str] = None,
                     sliver_state: list[str] = None, component_type: list[str] = None,
                     component_model: list[str] = None, bdf: list[str] = None, vlan: list[str] = None,
                     ip_subnet: list[str] = None, site: list[str] = None, host: list[str] = None,
                     exclude_user_id: list[str] = None, exclude_user_email: list[str] = None,
                     exclude_project_id: list[str] = None, exclude_site: list[str] = None, facility: list[str] = None,
                     exclude_host: list[str] = None, exclude_slice_state: list[str] = None,
                     exclude_sliver_state: list[str] = None,
                     page=0, per_page=1000, fetch_all=True):
        """
        Fetch slices with optional filters. Supports fetching all pages or just one.

        :param start_time: Filter by start time (inclusive)
        :type start_time: str
        :param end_time: Filter by end time (inclusive)
        :type end_time: str
        :param user_id: Filter by user uuid
        :type user_id: List[str]
        :param user_email: Filter by user email
        :type user_email: List[str]
        :param project_id: Filter by project uuid
        :type project_id: List[str]
        :param slice_id: Filter by slice uuid
        :type slice_id: List[str]
        :param slice_state: Filter by slice state; allowed values Nascent, Configuring, StableError, StableOK, Closing, Dead, Modifying, ModifyOK, ModifyError, AllocatedError, AllocatedOK
        :type slice_state: List[str]
        :param sliver_id: Filter by sliver uuid
        :type sliver_id: List[str]
        :param sliver_type: Filter by sliver type; allowed values VM, Switch, Facility, L2STS, L2PTP, L2Bridge, FABNetv4, FABNetv6, PortMirror, L3VPN, FABNetv4Ext, FABNetv6Ext
        :type sliver_type: List[str]
        :param sliver_state: Filter by sliver state; allowed values Nascent, Ticketed, Active, ActiveTicketed, Closed, CloseWait, Failed, Unknown, CloseFail
        :type sliver_state: List[str]
        :param component_type: Filter by component type, allowed values GPU, SmartNIC, SharedNIC, FPGA, NVME, Storage
        :type component_type: List[str]
        :param component_model: Filter by component model
        :type component_model: List[str]
        :param bdf: Filter by specified BDF (Bus:Device.Function) of interfaces/components
        :type bdf: List[str]
        :param vlan: Filter by VLAN associated with their sliver interfaces.
        :type vlan: List[str]
        :param ip_subnet: Filter by specified IP subnet
        :type ip_subnet: List[str]
        :param site: Filter by site
        :type site: List[str]
        :param host: Filter by host
        :type host: List[str]
        :param host: Filter by host
        :type host: List[str]
        :param exclude_user_id: Exclude Users by IDs
        :type exclude_user_id: List[str]
        :param exclude_user_email: Exclude Users by emails
        :type exclude_user_email: List[str]
        :param exclude_project_id: Exclude projects
        :type exclude_project_id: List[str]
        :param exclude_site: Exclude sites
        :type exclude_site: List[str]
        :param exclude_host: Exclude hosts
        :type exclude_host: List[str]
        :param exclude_slice_state: Filter by slice state; allowed values Nascent, Configuring, StableError, StableOK, Closing, Dead, Modifying, ModifyOK, ModifyError, AllocatedError, AllocatedOK
        :type exclude_slice_state: List[str]
        :param exclude_sliver_state: Filter by sliver state; allowed values Nascent, Ticketed, Active, ActiveTicketed, Closed, CloseWait, Failed, Unknown, CloseFail
        :type exclude_sliver_state: List[str]
        :param page: Page number for pagination. Default is 1.
        :type page: int
        :param per_page: Number of records per page. Default is 10.
        :type per_page: int
        :param fetch_all: If True, paginates until all results are fetched.
        :return: Dict with 'total' and 'data' keys.
        """
        all_slices = []
        total = 0
        url = f"{self.base_url}/slices"

        base_params = {
            "start_time": start_time,
            "end_time": end_time,
            "user_id": user_id,
            "user_email": user_email,
            "project_id": project_id,
            "slice_id": slice_id,
            "slice_state": slice_state,
            "sliver_id": sliver_id,
            "sliver_type": sliver_type,
            "sliver_state": sliver_state,
            "component_type": component_type,
            "component_model": component_model,
            "bdf": bdf,
            "vlan": vlan,
            "ip_subnet": ip_subnet,
            "site": site,
            "host": host,
            "facility": facility,
            "exclude_user_id": exclude_user_id,
            "exclude_user_email": exclude_user_email,
            "exclude_project_id": exclude_project_id,
            "exclude_site": exclude_site,
            "exclude_host": exclude_host,
            "exclude_slice_state": exclude_slice_state,
            "exclude_sliver_state": exclude_sliver_state,
            "per_page": per_page  # page will be added per iteration
        }

        # Remove keys with None values
        filtered_params = {k: v for k, v in base_params.items() if v is not None}

        while True:
            filtered_params["page"] = page
            response = requests.get(url, headers=self.headers, params=filtered_params)

            if response.status_code == 200:
                response = response.json()
            else:
                raise Exception(f"Failed to fetch slices: {response.status_code} - {response.text}")

            if page == 0:
                total = response.get("total")

            data = response.get("data", [])
            all_slices.extend(data)

            if not fetch_all or not data or len(all_slices) >= total:
                break

            page += 1

        return {
            "total": total,
            "data": all_slices
        }

    def query_slivers(self, start_time: str = None, end_time: str = None, user_id: list[str] = None,
                      user_email: list[str] = None, project_id: list[str] = None, slice_id: list[str] = None,
                      slice_state: list[str] = None, sliver_id: list[str] = None, sliver_type: list[str] = None,
                      sliver_state: list[str] = None, component_type: list[str] = None,
                      component_model: list[str] = None, bdf: list[str] = None, vlan: list[str] = None,
                      ip_subnet: list[str] = None, site: list[str] = None, host: list[str] = None,
                      exclude_user_id: list[str] = None, exclude_user_email: list[str] = None,
                      exclude_project_id: list[str] = None, exclude_site: list[str] = None, facility: list[str] = None,
                      exclude_host: list[str] = None, exclude_slice_state: list[str] = None,
                     exclude_sliver_state: list[str] = None, page=0, per_page=1000, fetch_all=True):
        """
        Fetch slivers with optional filters. Supports fetching all pages or just one.

        :param start_time: Filter by start time (inclusive)
        :type start_time: str
        :param end_time: Filter by end time (inclusive)
        :type end_time: str
        :param user_id: Filter by user uuid
        :type user_id: List[str]
        :param user_email: Filter by user email
        :type user_email: List[str]
        :param project_id: Filter by project uuid
        :type project_id: List[str]
        :param slice_id: Filter by slice uuid
        :type slice_id: List[str]
        :param slice_state: Filter by slice state; allowed values Nascent, Configuring, StableError, StableOK, Closing, Dead, Modifying, ModifyOK, ModifyError, AllocatedError, AllocatedOK
        :type slice_state: List[str]
        :param sliver_id: Filter by sliver uuid
        :type sliver_id: List[str]
        :param sliver_type: Filter by sliver type; allowed values VM, Switch, Facility, L2STS, L2PTP, L2Bridge, FABNetv4, FABNetv6, PortMirror, L3VPN, FABNetv4Ext, FABNetv6Ext
        :type sliver_type: List[str]
        :param sliver_state: Filter by sliver state; allowed values Nascent, Ticketed, Active, ActiveTicketed, Closed, CloseWait, Failed, Unknown, CloseFail
        :type sliver_state: List[str]
        :param component_type: Filter by component type, allowed values GPU, SmartNIC, SharedNIC, FPGA, NVME, Storage
        :type component_type: List[str]
        :param component_model: Filter by component model
        :type component_model: List[str]
        :param bdf: Filter by specified BDF (Bus:Device.Function) of interfaces/components
        :type bdf: List[str]
        :param vlan: Filter by VLAN associated with their sliver interfaces.
        :type vlan: List[str]
        :param ip_subnet: Filter by specified IP subnet
        :type ip_subnet: List[str]
        :param site: Filter by site
        :type site: List[str]
        :param host: Filter by host
        :type host: List[str]
        :param host: Filter by host
        :type host: List[str]
        :param exclude_user_id: Exclude Users by IDs
        :type exclude_user_id: List[str]
        :param exclude_user_email: Exclude Users by emails
        :type exclude_user_email: List[str]
        :param exclude_project_id: Exclude projects
        :type exclude_project_id: List[str]
        :param exclude_site: Exclude sites
        :type exclude_site: List[str]
        :param exclude_host: Exclude hosts
        :type exclude_host: List[str]
        :param exclude_slice_state: Filter by slice state; allowed values Nascent, Configuring, StableError, StableOK, Closing, Dead, Modifying, ModifyOK, ModifyError, AllocatedError, AllocatedOK
        :type exclude_slice_state: List[str]
        :param exclude_sliver_state: Filter by sliver state; allowed values Nascent, Ticketed, Active, ActiveTicketed, Closed, CloseWait, Failed, Unknown, CloseFail
        :type exclude_sliver_state: List[str]
        :param page: Page number for pagination. Default is 1.
        :type page: int
        :param per_page: Number of records per page. Default is 10.
        :type per_page: int

        :param fetch_all: If True, paginates until all results are fetched.
        :return: Dict with 'total' and 'data' keys.
        """
        all_slivers = []
        total = 0
        url = f"{self.base_url}/slivers"

        base_params = {
            "start_time": start_time,
            "end_time": end_time,
            "user_id": user_id,
            "user_email": user_email,
            "project_id": project_id,
            "slice_id": slice_id,
            "slice_state": slice_state,
            "sliver_id": sliver_id,
            "sliver_type": sliver_type,
            "sliver_state": sliver_state,
            "component_type": component_type,
            "component_model": component_model,
            "bdf": bdf,
            "vlan": vlan,
            "ip_subnet": ip_subnet,
            "site": site,
            "host": host,
            "facility": facility,
            "exclude_user_id": exclude_user_id,
            "exclude_user_email": exclude_user_email,
            "exclude_project_id": exclude_project_id,
            "exclude_site": exclude_site,
            "exclude_host": exclude_host,
            "exclude_slice_state": exclude_slice_state,
            "exclude_sliver_state": exclude_sliver_state,
            "per_page": per_page  # page will be added per iteration
        }

        # Remove keys with None values
        filtered_params = {k: v for k, v in base_params.items() if v is not None}

        while True:
            filtered_params["page"] = page
            response = requests.get(url, headers=self.headers, params=filtered_params)

            if response.status_code == 200:
                response = response.json()
            else:
                raise Exception(f"Failed to fetch slices: {response.status_code} - {response.text}")

            if page == 0:
                total = response.get("total")

            data = response.get("data", [])
            all_slivers.extend(data)

            if not fetch_all or not data or len(all_slivers) >= total:
                break

            page += 1

        return {
            "total": total,
            "data": all_slivers
        }

    def query_users(self, start_time: str = None, end_time: str = None, user_id: list[str] = None,
                    user_email: list[str] = None, project_id: list[str] = None, slice_id: list[str] = None,
                    slice_state: list[str] = None, sliver_id: list[str] = None, sliver_type: list[str] = None,
                    sliver_state: list[str] = None, component_type: list[str] = None,
                    component_model: list[str] = None, bdf: list[str] = None, vlan: list[str] = None,
                    ip_subnet: list[str] = None, site: list[str] = None, host: list[str] = None,
                    exclude_user_id: list[str] = None, exclude_user_email: list[str] = None,
                    exclude_project_id: list[str] = None, exclude_site: list[str] = None, facility: list[str] = None,
                    exclude_host: list[str] = None, exclude_slice_state: list[str] = None,
                    exclude_sliver_state: list[str] = None, user_active: bool = None, project_type: list[str] = None,
                    exclude_project_type: list[str] = None, page=0, per_page=1000, fetch_all=True):
        """
        Fetch users with optional filters. Supports fetching all pages or just one.

        :param start_time: Filter by start time (inclusive)
        :type start_time: str
        :param end_time: Filter by end time (inclusive)
        :type end_time: str
        :param user_id: Filter by user uuid
        :type user_id: List[str]
        :param user_email: Filter by user email
        :type user_email: List[str]
        :param project_id: Filter by project uuid
        :type project_id: List[str]
        :param slice_id: Filter by slice uuid
        :type slice_id: List[str]
        :param slice_state: Filter by slice state; allowed values Nascent, Configuring, StableError, StableOK, Closing, Dead, Modifying, ModifyOK, ModifyError, AllocatedError, AllocatedOK
        :type slice_state: List[str]
        :param sliver_id: Filter by sliver uuid
        :type sliver_id: List[str]
        :param sliver_type: Filter by sliver type; allowed values VM, Switch, Facility, L2STS, L2PTP, L2Bridge, FABNetv4, FABNetv6, PortMirror, L3VPN, FABNetv4Ext, FABNetv6Ext
        :type sliver_type: List[str]
        :param sliver_state: Filter by sliver state; allowed values Nascent, Ticketed, Active, ActiveTicketed, Closed, CloseWait, Failed, Unknown, CloseFail
        :type sliver_state: List[str]
        :param component_type: Filter by component type, allowed values GPU, SmartNIC, SharedNIC, FPGA, NVME, Storage
        :type component_type: List[str]
        :param component_model: Filter by component model
        :type component_model: List[str]
        :param bdf: Filter by specified BDF (Bus:Device.Function) of interfaces/components
        :type bdf: List[str]
        :param vlan: Filter by VLAN associated with their sliver interfaces.
        :type vlan: List[str]
        :param ip_subnet: Filter by specified IP subnet
        :type ip_subnet: List[str]
        :param site: Filter by site
        :type site: List[str]
        :param host: Filter by host
        :type host: List[str]
        :param host: Filter by host
        :type host: List[str]
        :param exclude_user_id: Exclude Users by IDs
        :type exclude_user_id: List[str]
        :param exclude_user_email: Exclude Users by emails
        :type exclude_user_email: List[str]
        :param exclude_project_id: Exclude projects
        :type exclude_project_id: List[str]
        :param exclude_site: Exclude sites
        :type exclude_site: List[str]
        :param exclude_host: Exclude hosts
        :type exclude_host: List[str]
        :param exclude_slice_state: Filter by slice state; allowed values Nascent, Configuring, StableError, StableOK, Closing, Dead, Modifying, ModifyOK, ModifyError, AllocatedError, AllocatedOK
        :type exclude_slice_state: List[str]
        :param exclude_sliver_state: Filter by sliver state; allowed values Nascent, Ticketed, Active, ActiveTicketed, Closed, CloseWait, Failed, Unknown, CloseFail
        :type exclude_sliver_state: List[str]
        :param user_active: Filter by whether the user is active
        :type user_active: bool
        :param project_type: List of project types to include (research, education, maintenance, tutorial)
        :param exclude_project_type: List of project types to exclude
        :param page: Page number for pagination. Default is 1.
        :type page: int
        :param per_page: Number of records per page. Default is 10.
        :type per_page: int

        :param fetch_all: If True, paginates until all results are fetched.
        :return: Dict with 'total' and 'data' keys.
        """
        all_users = []
        total = 0
        url = f"{self.base_url}/users"

        base_params = {
            "start_time": start_time,
            "end_time": end_time,
            "user_id": user_id,
            "user_email": user_email,
            "project_id": project_id,
            "slice_id": slice_id,
            "slice_state": slice_state,
            "sliver_id": sliver_id,
            "sliver_type": sliver_type,
            "sliver_state": sliver_state,
            "component_type": component_type,
            "component_model": component_model,
            "bdf": bdf,
            "vlan": vlan,
            "ip_subnet": ip_subnet,
            "site": site,
            "host": host,
            "facility": facility,
            "project_type": project_type,
            "user_active": user_active,
            "exclude_user_id": exclude_user_id,
            "exclude_user_email": exclude_user_email,
            "exclude_project_id": exclude_project_id,
            "exclude_site": exclude_site,
            "exclude_host": exclude_host,
            "exclude_slice_state": exclude_slice_state,
            "exclude_sliver_state": exclude_sliver_state,
            "exclude_project_type": exclude_project_type,
            "per_page": per_page  # page will be added per iteration
        }

        # Remove keys with None values
        filtered_params = {k: v for k, v in base_params.items() if v is not None}

        while True:
            filtered_params["page"] = page
            response = requests.get(url, headers=self.headers, params=filtered_params)

            if response.status_code == 200:
                response = response.json()
            else:
                raise Exception(f"Failed to fetch slices: {response.status_code} - {response.text}")

            if page == 0:
                total = response.get("total")

            data = response.get("data", [])
            all_users.extend(data)

            if not fetch_all or not data or len(all_users) >= total:
                break

            page += 1

        return {
            "total": total,
            "data": all_users
        }

    def query_projects(self, start_time: str = None, end_time: str = None, user_id: list[str] = None,
                       user_email: list[str] = None, project_id: list[str] = None, slice_id: list[str] = None,
                       slice_state: list[str] = None, sliver_id: list[str] = None, sliver_type: list[str] = None,
                       sliver_state: list[str] = None, component_type: list[str] = None,
                       component_model: list[str] = None, bdf: list[str] = None, vlan: list[str] = None,
                       ip_subnet: list[str] = None, site: list[str] = None, host: list[str] = None,
                       exclude_user_id: list[str] = None, exclude_user_email: list[str] = None,
                       exclude_project_id: list[str] = None, exclude_site: list[str] = None, facility: list[str] = None,
                       exclude_host: list[str] = None, exclude_slice_state: list[str] = None,
                       exclude_sliver_state: list[str] = None, project_active: bool = None, project_type: list[str] = None,
                       exclude_project_type: list[str] = None, page=0, per_page=1000, fetch_all=True):
        """
        Fetch projects with optional filters. Supports fetching all pages or just one.

        :param start_time: Filter by start time (inclusive)
        :type start_time: str
        :param end_time: Filter by end time (inclusive)
        :type end_time: str
        :param user_id: Filter by user uuid
        :type user_id: List[str]
        :param user_email: Filter by user email
        :type user_email: List[str]
        :param project_id: Filter by project uuid
        :type project_id: List[str]
        :param slice_id: Filter by slice uuid
        :type slice_id: List[str]
        :param slice_state: Filter by slice state; allowed values Nascent, Configuring, StableError, StableOK, Closing, Dead, Modifying, ModifyOK, ModifyError, AllocatedError, AllocatedOK
        :type slice_state: List[str]
        :param sliver_id: Filter by sliver uuid
        :type sliver_id: List[str]
        :param sliver_type: Filter by sliver type; allowed values VM, Switch, Facility, L2STS, L2PTP, L2Bridge, FABNetv4, FABNetv6, PortMirror, L3VPN, FABNetv4Ext, FABNetv6Ext
        :type sliver_type: List[str]
        :param sliver_state: Filter by sliver state; allowed values Nascent, Ticketed, Active, ActiveTicketed, Closed, CloseWait, Failed, Unknown, CloseFail
        :type sliver_state: List[str]
        :param component_type: Filter by component type, allowed values GPU, SmartNIC, SharedNIC, FPGA, NVME, Storage
        :type component_type: List[str]
        :param component_model: Filter by component model
        :type component_model: List[str]
        :param bdf: Filter by specified BDF (Bus:Device.Function) of interfaces/components
        :type bdf: List[str]
        :param vlan: Filter by VLAN associated with their sliver interfaces.
        :type vlan: List[str]
        :param ip_subnet: Filter by specified IP subnet
        :type ip_subnet: List[str]
        :param site: Filter by site
        :type site: List[str]
        :param host: Filter by host
        :type host: List[str]
        :param host: Filter by host
        :type host: List[str]
        :param exclude_user_id: Exclude Users by IDs
        :type exclude_user_id: List[str]
        :param exclude_user_email: Exclude Users by emails
        :type exclude_user_email: List[str]
        :param exclude_project_id: Exclude projects
        :type exclude_project_id: List[str]
        :param exclude_site: Exclude sites
        :type exclude_site: List[str]
        :param exclude_host: Exclude hosts
        :type exclude_host: List[str]
        :param exclude_slice_state: Filter by slice state; allowed values Nascent, Configuring, StableError, StableOK, Closing, Dead, Modifying, ModifyOK, ModifyError, AllocatedError, AllocatedOK
        :type exclude_slice_state: List[str]
        :param exclude_sliver_state: Filter by sliver state; allowed values Nascent, Ticketed, Active, ActiveTicketed, Closed, CloseWait, Failed, Unknown, CloseFail
        :type exclude_sliver_state: List[str]
        :param project_active: Filter by whether the project is active
        :type project_active: bool
        :param project_type: List of project types to include (research, education, maintenance, tutorial)
        :param exclude_project_type: List of project types to exclude

        :param page: Page number for pagination. Default is 1.
        :type page: int
        :param per_page: Number of records per page. Default is 10.
        :type per_page: int

        :param fetch_all: If True, paginates until all results are fetched.
        :return: Dict with 'total' and 'data' keys.
        """
        all_projects = []
        total = 0
        url = f"{self.base_url}/projects"

        base_params = {
            "start_time": start_time,
            "end_time": end_time,
            "user_id": user_id,
            "user_email": user_email,
            "project_id": project_id,
            "slice_id": slice_id,
            "slice_state": slice_state,
            "sliver_id": sliver_id,
            "sliver_type": sliver_type,
            "sliver_state": sliver_state,
            "component_type": component_type,
            "component_model": component_model,
            "bdf": bdf,
            "vlan": vlan,
            "ip_subnet": ip_subnet,
            "site": site,
            "host": host,
            "facility": facility,
            "project_type": project_type,
            "project_active": project_active,
            "exclude_user_id": exclude_user_id,
            "exclude_user_email": exclude_user_email,
            "exclude_project_id": exclude_project_id,
            "exclude_site": exclude_site,
            "exclude_host": exclude_host,
            "exclude_slice_state": exclude_slice_state,
            "exclude_sliver_state": exclude_sliver_state,
            "exclude_project_type": exclude_project_type,
            "per_page": per_page  # page will be added per iteration
        }

        # Remove keys with None values
        filtered_params = {k: v for k, v in base_params.items() if v is not None}

        while True:
            filtered_params["page"] = page
            response = requests.get(url, headers=self.headers, params=filtered_params)

            if response.status_code == 200:
                response = response.json()
            else:
                raise Exception(f"Failed to fetch slices: {response.status_code} - {response.text}")

            if page == 0:
                total = response.get("total")

            data = response.get("data", [])
            all_projects.extend(data)

            if not fetch_all or not data or len(all_projects) >= total:
                break

            page += 1

        return {
            "total": total,
            "data": all_projects
        }

    def post_sliver(self, slice_id: str, sliver_id: str, sliver_payload: dict):
        """
        Create or update a sliver for a given slice ID and sliver ID.

        :param slice_id: UUID of the slice
        :type slice_id: str
        :param sliver_id: UUID of the sliver
        :type sliver_id: str
        :param sliver_payload: Dictionary containing the sliver specification
        :type sliver_payload: dict
        :return: Server response as a dictionary
        :rtype: dict

        Example sliver dictionary:
            sliver_payload = {
                "project_id": "d78f130a-29b2-4f78-b9a9-87828d6cb2e2",
                "project_name": "Edge AI Project",
                "slice_id": "a3f41e9a-7e2b-4df7-baf7-12f48a3c8e6f",
                "slice_name": "edge-ai-slice",
                "user_id": "u98f124b-2332-483f-92b7-3bfbfb06b6e0",
                "user_email": "alice@example.com",
                "host": "host1.edge.fabric",
                "site": "RENC",
                "sliver_id": "c9d3f9b2-cc40-44b0-ae3a-f3a9f7a87771",
                "node_id": "n1",
                "state": "Active",
                "sliver_type": "VM",
                "ip_subnet": "192.168.1.0/24",
                "error": None,
                "image": "ubuntu-22.04",
                "core": 4,
                "ram": 8192,
                "disk": 100,
                "bandwidth": 10000,
                "lease_start": "2025-05-01T12:00:00Z",
                "lease_end": "2025-05-03T12:00:00Z",
                "components": [
                    {
                        "component_id": "comp-01",
                        "node_id": "n1",
                        "component_node_id": "gpu-node-1",
                        "type": "GPU",
                        "model": "A100",
                        "bdfs": ["0000:65:00.0", "0000:65:00.1"]
                    }
                ],
                "interfaces": [
                    {
                        "interface_id": "eth0",
                        "site": "RENC",
                        "vlan": "123",
                        "bdf": "0000:3b:00.0",
                        "local_name": "ens3",
                        "device_name": "mlx5_0",
                        "name": "mgmt-net"
                    }
                ]
            }
        """
        url = f"{self.base_url}/slivers/{slice_id}/{sliver_id}"

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"

        response = requests.post(url, headers=headers, json=sliver_payload)

        if response.status_code in (200, 201):
            return response.json()
        else:
            raise Exception(f"Failed to post sliver: {response.status_code} - {response.text}")

    def post_slice(self, slice_id: str, slice_payload: dict):
        """
        Create or update a slice.

        :param slice_id: UUID of the slice
        :type slice_id: str
        :param slice_payload: Dictionary containing the slice specification
        :type slice_payload: dict
        :return: Server response as a dictionary
        :rtype: dict

        Example slice_payload:
        slice_payload = {
            "project_id": "d78f130a-29b2-4f78-b9a9-87828d6cb2e2",
            "user_id": "u98f124b-2332-483f-92b7-3bfbfb06b6e0",
            "slice_id": "a3f41e9a-7e2b-4df7-baf7-12f48a3c8e6f",
            "slice_name": "edge-ai-slice",
            "state": "StableOK",
            "lease_start": "2025-05-01T12:00:00Z",
            "lease_end": "2025-05-03T12:00:00Z"
        }
        """
        url = f"{self.base_url}/slices/{slice_id}"

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"

        response = requests.post(url, headers=headers, json=slice_payload)

        if response.status_code in (200, 201):
            return response.json()
        else:
            raise Exception(f"Failed to post slice: {response.status_code} - {response.text}")

    def query_user_memberships(self,
                               start_time: str = None,
                               end_time: str = None,
                               user_id: list[str] = None,
                               user_email: list[str] = None,
                               exclude_user_id: list[str] = None,
                               exclude_user_email: list[str] = None,
                               project_type: list[str] = None,
                               exclude_project_type: list[str] = None,
                               project_active: bool = None,
                               project_expired: bool = None,
                               project_retired: bool = None,
                               user_active: bool = None,
                               page: int = 0,
                               per_page: int = 500,
                               fetch_all: bool = True):
        """
        Query user-project memberships with optional filters and pagination.

        :param start_time: Filter by start time (inclusive, ISO 8601 string)
        :param end_time: Filter by end time (inclusive, ISO 8601 string)
        :param user_id: List of user UUIDs to include
        :param user_email: List of user emails to include
        :param exclude_user_id: List of user UUIDs to exclude
        :param exclude_user_email: List of user emails to exclude
        :param project_type: List of project types to include (research, education, maintenance, tutorial)
        :param exclude_project_type: List of project types to exclude
        :param project_active: Filter by whether the project is active
        :param project_expired: Filter by whether the project is expired
        :param project_retired: Filter by whether the project is retired
        :param user_active: Filter by whether the user is active
        :param page: Page number for pagination (default: 0)
        :param per_page: Number of records per page (default: 200)
        :param fetch_all: If True, automatically paginates through all results
        :return: Dict with 'total' and 'data' keys
        """
        all_memberships = []
        total = 0
        url = f"{self.base_url}/users/memberships"

        base_params = {
            "start_time": start_time,
            "end_time": end_time,
            "user_id": user_id,
            "user_email": user_email,
            "exclude_user_id": exclude_user_id,
            "exclude_user_email": exclude_user_email,
            "project_type": project_type,
            "exclude_project_type": exclude_project_type,
            "project_active": project_active,
            "project_expired": project_expired,
            "project_retired": project_retired,
            "user_active": user_active,
            "per_page": per_page
        }

        # Filter out None values
        filtered_params = {k: v for k, v in base_params.items() if v is not None}

        while True:
            filtered_params["page"] = page
            response = requests.get(url, headers=self.headers, params=filtered_params)

            if response.status_code == 200:
                result = response.json()
            else:
                raise Exception(f"Failed to fetch memberships: {response.status_code} - {response.text}")

            if page == 0:
                total = result.get("total", 0)

            data = result.get("data", [])
            all_memberships.extend(data)

            if not fetch_all or not data or len(all_memberships) >= total:
                break

            page += 1

        return {
            "total": total,
            "data": all_memberships
        }

    def query_project_memberships(self,
                                  start_time: str = None,
                                  end_time: str = None,
                                  project_id: list[str] = None,
                                  exclude_project_id: list[str] = None,
                                  project_type: list[str] = None,
                                  exclude_project_type: list[str] = None,
                                  project_active: bool = None,
                                  project_expired: bool = None,
                                  project_retired: bool = None,
                                  user_active: bool = None,
                                  page: int = 0,
                                  per_page: int = 500,
                                  fetch_all: bool = True):
        """
        Query project-user memberships with optional filters and pagination.

        :param start_time: Filter by start time (ISO 8601 string)
        :param end_time: Filter by end time (ISO 8601 string)
        :param project_id: List of project UUIDs to include
        :param exclude_project_id: List of project UUIDs to exclude
        :param project_type: List of project types to include (research, education, maintenance, tutorial)
        :param exclude_project_type: List of project types to exclude
        :param project_active: Filter by whether project is active
        :param project_expired: Filter by whether project is expired
        :param project_retired: Filter by whether project is retired
        :param user_active: Filter by whether the user is active
        :param page: Page number for pagination (default: 0)
        :param per_page: Records per page (default: 200)
        :param fetch_all: If True, automatically paginate through all results
        :return: Dict with 'total' and 'data' keys
        """
        all_memberships = []
        total = 0
        url = f"{self.base_url}/projects/memberships"

        base_params = {
            "start_time": start_time,
            "end_time": end_time,
            "project_id": project_id,
            "exclude_project_id": exclude_project_id,
            "project_type": project_type,
            "exclude_project_type": exclude_project_type,
            "project_active": project_active,
            "project_expired": project_expired,
            "project_retired": project_retired,
            "user_active": user_active,
            "per_page": per_page  # page will be added dynamically
        }

        # Filter out None values
        filtered_params = {k: v for k, v in base_params.items() if v is not None}

        while True:
            filtered_params["page"] = page
            response = requests.get(url, headers=self.headers, params=filtered_params)

            if response.status_code == 200:
                result = response.json()
            else:
                raise Exception(f"Failed to fetch project memberships: {response.status_code} - {response.text}")

            if page == 0:
                total = result.get("total", 0)

            data = result.get("data", [])
            all_memberships.extend(data)

            if not fetch_all or not data or len(all_memberships) >= total:
                break

            page += 1

        return {
            "total": total,
            "data": all_memberships
        }
