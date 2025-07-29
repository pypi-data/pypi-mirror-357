# Python OTOBO Client Library

An asynchronous Python client for interacting with the OTOBO REST API. Built with `httpx` and `pydantic` for type safety and ease of use.

## Features

* **Asynchronous** HTTP requests using `httpx.AsyncClient`
* **Pydantic** models for request and response data validation
* Full CRUD operations for tickets:

  * `TicketCreate`
  * `TicketSearch`
  * `TicketGet`
  * `TicketUpdate`
  * `TicketHistoryGet`
* **Error handling** via `OTOBOError` for API errors
* Utility method `search_and_get` to combine search results with detailed retrieval

## Installation

Install from PyPI:

```bash
pip install otobo
```
## Quickstart

### 1. Configure the client

```python
from otobo import TicketOperation, OTOBOClientConfig
from otobo import AuthData

config = OTOBOClientConfig(
    base_url="https://your-otobo-server/nph-genericinterface.pl",
    service="OTOBO",
    auth=AuthData(UserLogin="root@localhost", Password="1234"),
    operations={
        TicketOperation.CREATE.value:    "ticket-create",
        TicketOperation.SEARCH.value:    "ticket-search",
        TicketOperation.GET.value:       "ticket-get",
        TicketOperation.UPDATE.value:    "ticket-update",
        TicketOperation.HISTORY_GET.value: "ticket-history-get",
    }
)
```

### 2. Initialize the client

```python
import logging
from httpx import AsyncClient
from otobo import OTOBOClient

logging.basicConfig(level=logging.INFO)

# Optionally inject your own AsyncClient
async_client = AsyncClient()

client = OTOBOClient(config, client=async_client)
```

### 3. Create a ticket

```python
from models.request_models import TicketCreateParams
from models.response_models import OTOBOTicketCreateResponse

payload = TicketCreateParams(
    Ticket={
        "Title": "New Order",
        "Queue": "Sales",
        "State": "new",
        "Priority": "3 normal",
        "CustomerUser": "customer@example.com"
    },
    Article={
        "Subject":  "Product Inquiry",
        "Body":     "Please send pricing details...",
        "MimeType": "text/plain"
    }
)

response: OTOBOTicketCreateResponse = await client.create_ticket(payload)
print(response.TicketID, response.TicketNumber)
```

### 4. Search and retrieve tickets

```python
from models.request_models import TicketSearchParams, TicketGetParams

search_params = TicketSearchParams(Title="%Order%")
search_res = await client.search_tickets(search_params)
ids = search_res.TicketID

for ticket_id in ids:
    get_params = TicketGetParams(TicketID=ticket_id, AllArticles=1)
    details = await client.get_ticket(get_params)
    print(details.Ticket[0])
```

### 5. Update a ticket

```python
from models.request_models import TicketUpdateParams

update_params = TicketUpdateParams(
    TicketID=response.TicketID,
    Ticket={"State": "closed"}
)
await client.update_ticket(update_params)
```

### 6. Get ticket history

```python
from models.request_models import TicketHistoryParams

history_params = TicketHistoryParams(TicketID=str(response.TicketID))
history_res = await client.get_ticket_history(history_params)
print(history_res.History)
```

### 7. Combined search and get

```python
from models.response_models import FullTicketSearchResponse

full_res: FullTicketSearchResponse = await client.search_and_get(search_params)
```


## License

MIT © Softoft, Tobias A. Bueck
