"""
External API Integration Services for TravelMaster

This module provides integration with real travel booking APIs
including flights, hotels, and activities.
"""

import asyncio
import httpx
from typing import List, Dict, Any, Optional, cast
from datetime import datetime, date
from decimal import Decimal
import os
from dataclasses import dataclass


@dataclass
class FlightSearchParams:
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date] = None
    passengers: int = 1
    max_price: Optional[Decimal] = None


@dataclass
class HotelSearchParams:
    destination: str
    check_in: date
    check_out: date
    guests: int = 1
    max_price_per_night: Optional[Decimal] = None


class FlightBookingAPI:
    """Integration with flight booking APIs (Amadeus, Skyscanner, etc.)"""
    
    def __init__(self):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Flight API Configuration (Real Flight Data)
        self.flight_api_key = os.getenv("FLIGHT_API_KEY")
        self.flight_api_secret = os.getenv("FLIGHT_API_SECRET") 
        
        # Amadeus backup configuration
        self.amadeus_key = os.getenv("AMADEUS_API_KEY")
        self.amadeus_secret = os.getenv("AMADEUS_API_SECRET")
        self.base_url = "https://test.api.amadeus.com"
        self.access_token = None
        self.token_endpoint_used = None  # Track which endpoint provided the token
        # Prefer Amadeus credentials for flight searches when present
        self.use_amadeus = False
        if self.amadeus_key and self.amadeus_secret:
            self.use_amadeus = True
            print("✅ Amadeus credentials detected — using Amadeus for flight searches")
        elif self.flight_api_key and self.flight_api_secret:
            print("✅ FLIGHT_API provider keys configured (non-Amadeus)")
        else:
            print("⚠️  No flight provider credentials found. Using mock data.")
            print("   Set AMADEUS_API_KEY/AMADEUS_API_SECRET or FLIGHT_API_KEY/FLIGHT_API_SECRET in .env file")
        
        # Airport mapping for common destinations
        self.airport_codes = {
            "paris": "CDG",
            "london": "LHR", 
            "tokyo": "NRT",
            "new york": "JFK",
            "los angeles": "LAX",
            "barcelona": "BCN",
            "rome": "FCO",
            "amsterdam": "AMS",
            "berlin": "BER",
            "madrid": "MAD"
        }
        
        self.airport_names = {
            "CDG": "Charles de Gaulle Airport",
            "LHR": "Heathrow Airport",
            "NRT": "Narita International Airport", 
            "JFK": "John F. Kennedy International Airport",
            "LAX": "Los Angeles International Airport",
            "BCN": "Barcelona-El Prat Airport",
            "FCO": "Leonardo da Vinci-Fiumicino Airport",
            "AMS": "Amsterdam Airport Schiphol",
            "BER": "Berlin Brandenburg Airport",
            "MAD": "Madrid-Barajas Airport"
        }
    
    def _get_airport_code(self, location: str) -> str:
        """Get airport code for a location"""
        location_lower = location.lower()
        for city, code in self.airport_codes.items():
            if city in location_lower:
                return code
        return location[:3].upper()  # Fallback to first 3 letters
    
    def _get_airport_name(self, location: str) -> str:
        """Get airport name for a location"""
        code = self._get_airport_code(location)
        return self.airport_names.get(code, f"{location} Airport")

    def _get_airline_name_from_code(self, carrier_code: str) -> str:
        """Convert simple airline IATA code to airline name"""
        mapping = {
            "AA": "American Airlines",
            "DL": "Delta Air Lines",
            "UA": "United Airlines",
            "BA": "British Airways",
            "AF": "Air France",
            "EK": "Emirates",
            "QR": "Qatar Airways",
            "MS": "EgyptAir",
        }
        if not carrier_code:
            return "Unknown Airline"
        return mapping.get(carrier_code.upper(), f"{carrier_code} Airlines")
    
    async def get_access_token(self) -> str:
        """Get OAuth access token for Amadeus API"""
        if self.access_token:
            return self.access_token

        try:
            # Try sandbox first (common for developer keys), then production
            token_endpoints = [
                "https://test.api.amadeus.com/v1/security/oauth2/token",
                "https://api.amadeus.com/v1/security/oauth2/token",
            ]

            data = {
                "grant_type": "client_credentials",
                "client_id": self.amadeus_key,
                "client_secret": self.amadeus_secret
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                for token_url in token_endpoints:
                    try:
                        resp = await client.post(token_url, data=data)
                    except Exception as e:
                        print(f"❌ Error requesting token from {token_url}: {e}")
                        continue

                    if resp.status_code == 200:
                        body = resp.json()
                        self.access_token = body.get("access_token")
                        self.token_endpoint_used = token_url  # Remember which endpoint worked
                        print(f"✅ Amadeus access token obtained from {token_url}")
                        return self.access_token
                    else:
                        # Print the first chunk of response to aid debugging
                        snippet = resp.text[:400].replace('\n', ' ')
                        print(f"❌ Amadeus token request to {token_url} failed: {resp.status_code} {snippet}")
        except Exception as e:
            print(f"❌ Error obtaining Amadeus token: {e}")

        # fallback
        self.access_token = "mock_access_token"
        return self.access_token
    
    async def search_flights(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """Search for flights using real Flight API"""
        try:
            # Prefer Amadeus integration when credentials are available
            if self.use_amadeus:
                print(f"✈️  Searching flights via Amadeus from {params.origin} to {params.destination}")
                return await self._real_flight_search(params)
            elif self.flight_api_key and self.flight_api_secret:
                print(f"✈️  Searching flights via configured Flight API provider from {params.origin} to {params.destination}")
                return await self._real_flight_search(params)
            else:
                print("✈️  Using mock flight data (No flight provider configured)")
                return await self._mock_flight_search(params)
                
        except Exception as e:
            print(f"❌ Flight search error: {e}")
            print("✈️  Falling back to mock flight data")
            return await self._mock_flight_search(params)
    
    async def _real_flight_search(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """Search for real flights using Amadeus Flight Offers API"""
        # Convert locations to airport codes
        origin_code = self._get_airport_code(params.origin)
        dest_code = self._get_airport_code(params.destination)
        departure_date = params.departure_date.strftime("%Y-%m-%d")

        try:
            token = await self.get_access_token()
            if not token or token == "mock_access_token":
                print("⚠️  No valid Amadeus token available, falling back to mock flights")
                return await self._mock_flight_search(params)

            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            # Use the same environment (test or production) that provided the token
            if self.token_endpoint_used and "test.api.amadeus.com" in self.token_endpoint_used:
                search_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
            else:
                search_url = "https://api.amadeus.com/v2/shopping/flight-offers"
            query = {
                "originLocationCode": origin_code,
                "destinationLocationCode": dest_code,
                "departureDate": departure_date,
                "adults": str(params.passengers),
                "max": "5",
                "currencyCode": "USD"
            }
            
            # Add return date for round-trip search
            if params.return_date:
                query["returnDate"] = params.return_date.strftime("%Y-%m-%d")
                print(f"🔄 Round-trip search: Return on {query['returnDate']}")

            print(f"🌐 Amadeus flight search: {origin_code} -> {dest_code} on {departure_date}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(search_url, headers=headers, params=query)
                print(f"✈️ Amadeus API status: {resp.status_code}")
                if resp.status_code != 200:
                    print(f"❌ Amadeus flight search failed: {resp.status_code} {resp.text[:300]}")
                    return await self._mock_flight_search(params)

                data = resp.json()
                offers = data.get("data", [])
                flights: List[Dict[str, Any]] = []

                for i, offer in enumerate(offers[:3]):  # Process top 3 offers
                    try:
                        itineraries = offer.get("itineraries", [])
                        if not itineraries:
                            continue

                        price_obj = offer.get("price", {})
                        total_price = float(price_obj.get("total", 0) or 0)

                        # Handle round-trip (2 itineraries) vs one-way (1 itinerary)
                        if len(itineraries) >= 2 and params.return_date:
                            # Round-trip: Create outbound and return flights
                            outbound_itin = itineraries[0]
                            return_itin = itineraries[1]
                            
                            # Process outbound flight
                            out_segments = outbound_itin.get("segments", [])
                            if out_segments:
                                out_seg = out_segments[0]
                                out_carrier = out_seg.get("carrierCode", "")
                                out_airline = self._get_airline_name_from_code(out_carrier)
                                out_departure = out_seg.get("departure", {})
                                out_arrival = out_seg.get("arrival", {})
                                
                                outbound_flight = {
                                    "id": f"amadeus_out_{i+1}",
                                    "airline": out_airline,
                                    "flight_number": f"{out_carrier}{out_seg.get('number', '')}",
                                    "aircraft": out_seg.get('aircraft', {}).get('code', 'Boeing 737') if isinstance(out_seg.get('aircraft', {}), dict) else out_seg.get('aircraft', 'Boeing 737'),
                                    "departure_time": out_departure.get("at", ""),
                                    "arrival_time": out_arrival.get("at", ""),
                                    "departure_airport": origin_code,  # Force correct outbound: origin -> destination
                                    "departure_airport_name": self._get_airport_name(params.origin),
                                    "arrival_airport": dest_code,
                                    "arrival_airport_name": self._get_airport_name(params.destination),
                                    "duration": outbound_itin.get("duration", ""),
                                    "price": total_price / 2,  # Split price between outbound and return
                                    "currency": price_obj.get("currency", "USD"),
                                    "stops": max(0, len(out_segments) - 1),
                                    "class": offer.get('travelerPricings', [{}])[0].get('fareDetailsBySegment', [{}])[0].get('cabin', 'Economy') if offer.get('travelerPricings') else 'Economy',
                                    "available_seats": offer.get('numberOfBookableSeats', 20),
                                    "instant_confirmation": True,
                                    "source": "amadeus_api",
                                    "trip_type": "outbound"
                                }
                                
                                if not params.max_price or outbound_flight["price"] <= float(params.max_price) / 2:
                                    flights.append(outbound_flight)
                            
                            # Process return flight
                            ret_segments = return_itin.get("segments", [])
                            if ret_segments:
                                ret_seg = ret_segments[0]
                                ret_carrier = ret_seg.get("carrierCode", "")
                                ret_airline = self._get_airline_name_from_code(ret_carrier)
                                ret_departure = ret_seg.get("departure", {})
                                ret_arrival = ret_seg.get("arrival", {})
                                
                                return_flight = {
                                    "id": f"amadeus_ret_{i+1}",
                                    "airline": ret_airline,
                                    "flight_number": f"{ret_carrier}{ret_seg.get('number', '')}",
                                    "aircraft": ret_seg.get('aircraft', {}).get('code', 'Boeing 737') if isinstance(ret_seg.get('aircraft', {}), dict) else ret_seg.get('aircraft', 'Boeing 737'),
                                    "departure_time": ret_departure.get("at", ""),
                                    "arrival_time": ret_arrival.get("at", ""),
                                    "departure_airport": dest_code,  # Force return: destination -> origin
                                    "departure_airport_name": self._get_airport_name(params.destination),
                                    "arrival_airport": origin_code,   # Force return: destination -> origin
                                    "arrival_airport_name": self._get_airport_name(params.origin),
                                    "duration": return_itin.get("duration", ""),
                                    "price": total_price / 2,  # Split price between outbound and return
                                    "currency": price_obj.get("currency", "USD"),
                                    "stops": max(0, len(ret_segments) - 1),
                                    "class": offer.get('travelerPricings', [{}])[0].get('fareDetailsBySegment', [{}])[0].get('cabin', 'Economy') if offer.get('travelerPricings') else 'Economy',
                                    "available_seats": offer.get('numberOfBookableSeats', 20),
                                    "instant_confirmation": True,
                                    "source": "amadeus_api",
                                    "trip_type": "return"
                                }
                                
                                if not params.max_price or return_flight["price"] <= float(params.max_price) / 2:
                                    flights.append(return_flight)
                        
                        else:
                            # One-way flight handling
                            first_itin = itineraries[0]
                            segments = first_itin.get("segments", [])
                            if not segments:
                                continue
                            first_seg = segments[0]

                            carrier = first_seg.get("carrierCode", "")
                            airline = self._get_airline_name_from_code(carrier)

                            departure = first_seg.get("departure", {})
                            arrival = first_seg.get("arrival", {})

                            flight_info = {
                                "id": f"amadeus_{i+1}",
                                "airline": airline,
                                "flight_number": f"{carrier}{first_seg.get('number', '')}",
                                "aircraft": first_seg.get('aircraft', {}).get('code', 'Boeing 737') if isinstance(first_seg.get('aircraft', {}), dict) else first_seg.get('aircraft', 'Boeing 737'),
                                "departure_time": departure.get("at", ""),
                                "arrival_time": arrival.get("at", ""),
                                "departure_airport": departure.get('iataCode', origin_code),
                                "arrival_airport": arrival.get('iataCode', dest_code),
                                "duration": first_itin.get("duration", ""),
                                "price": total_price,
                                "currency": price_obj.get("currency", "USD"),
                                "stops": max(0, len(segments) - 1),
                                "class": offer.get('travelerPricings', [{}])[0].get('fareDetailsBySegment', [{}])[0].get('cabin', 'Economy') if offer.get('travelerPricings') else 'Economy',
                                "available_seats": offer.get('numberOfBookableSeats', 20),
                                "instant_confirmation": True,
                                "source": "amadeus_api",
                                "trip_type": "one_way"
                            }

                            if not params.max_price or flight_info["price"] <= float(params.max_price):
                                flights.append(flight_info)
                    except Exception as item_err:
                        print(f"⚠️  Error parsing Amadeus offer: {item_err}")
                        continue

                if flights:
                    print(f"✅ Found {len(flights)} flights via Amadeus")
                    # Debug: show flight details
                    for flight in flights:
                        print(f"   {flight.get('trip_type', 'unknown').upper()}: {flight.get('departure_airport')} -> {flight.get('arrival_airport')} ({flight.get('flight_number')})")
                    return flights
                else:
                    print("⚠️  No offers from Amadeus, falling back to mock flights")
                    return await self._mock_flight_search(params)

        except Exception as e:
            print(f"❌ Error during Amadeus flight search: {e}")
            return await self._mock_flight_search(params)

    async def _mock_flight_search(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """Mock flight search results for development with proper round-trip support"""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        base_price = min(params.max_price or Decimal("800"), Decimal("600"))
        origin_code = self._get_airport_code(params.origin)
        dest_code = self._get_airport_code(params.destination)
        
        flights = []
        
        # Outbound flights
        outbound_flights = [
            {
                "id": "mock_out_001",
                "airline": "American Airlines",
                "flight_number": "AA1234",
                "departure_airport": origin_code,
                "departure_airport_name": self._get_airport_name(params.origin),
                "arrival_airport": dest_code,
                "arrival_airport_name": self._get_airport_name(params.destination),
                "departure_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=8)),
                "arrival_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=14, minute=30)),
                "duration": "6h 30m",
                "stops": 0,
                "price": base_price * Decimal("0.45"),  # Half price for outbound
                "currency": "USD",
                "class": "Economy",
                "available_seats": 15,
                "aircraft": "Boeing 737-800",
                "trip_type": "outbound",
                "source": "mock_api"
            },
            {
                "id": "mock_out_002", 
                "airline": "Delta Air Lines",
                "flight_number": "DL5678",
                "departure_airport": origin_code,
                "departure_airport_name": self._get_airport_name(params.origin),
                "arrival_airport": dest_code,
                "arrival_airport_name": self._get_airport_name(params.destination),
                "departure_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=12)),
                "arrival_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=20, minute=45)),
                "duration": "8h 45m",
                "stops": 1,
                "price": base_price * Decimal("0.375"),  # Half price for outbound
                "currency": "USD",
                "class": "Economy",
                "available_seats": 8,
                "aircraft": "Airbus A320",
                "trip_type": "outbound",
                "source": "mock_api"
            }
        ]
        
        flights.extend(outbound_flights)
        
        # Return flights (if round-trip)
        if params.return_date:
            return_flights = [
                {
                    "id": "mock_ret_001",
                    "airline": "American Airlines",
                    "flight_number": "AA4321",
                    "departure_airport": dest_code,  # Return: destination -> origin
                    "departure_airport_name": self._get_airport_name(params.destination),
                    "arrival_airport": origin_code,
                    "arrival_airport_name": self._get_airport_name(params.origin),
                    "departure_time": datetime.combine(params.return_date, datetime.min.time().replace(hour=10)),
                    "arrival_time": datetime.combine(params.return_date, datetime.min.time().replace(hour=16, minute=45)),
                    "duration": "6h 45m",
                    "stops": 0,
                    "price": base_price * Decimal("0.45"),  # Half price for return
                    "currency": "USD",
                    "class": "Economy",
                    "available_seats": 18,
                    "aircraft": "Boeing 737-800",
                    "trip_type": "return",
                    "source": "mock_api"
                },
                {
                    "id": "mock_ret_002", 
                    "airline": "Delta Air Lines",
                    "flight_number": "DL8765",
                    "departure_airport": dest_code,  # Return: destination -> origin
                    "departure_airport_name": self._get_airport_name(params.destination),
                    "arrival_airport": origin_code,
                    "arrival_airport_name": self._get_airport_name(params.origin),
                    "departure_time": datetime.combine(params.return_date, datetime.min.time().replace(hour=15)),
                    "arrival_time": datetime.combine(params.return_date, datetime.min.time().replace(hour=23, minute=30)),
                    "duration": "8h 30m",
                    "stops": 1,
                    "price": base_price * Decimal("0.375"),  # Half price for return
                    "currency": "USD",
                    "class": "Economy",
                    "available_seats": 12,
                    "aircraft": "Airbus A320",
                    "trip_type": "return",
                    "source": "mock_api"
                }
            ]
            
            flights.extend(return_flights)
        
        # Debug: show mock flight details
        if flights:
            print(f"✅ Created {len(flights)} mock flights")
            for flight in flights:
                print(f"   {flight.get('trip_type', 'unknown').upper()}: {flight.get('departure_airport')} -> {flight.get('arrival_airport')} ({flight.get('flight_number')})")
        
        return flights


class HotelBookingAPI:
    """Integration with hotel booking APIs (Amadeus, Booking.com, etc.)"""
    
    def __init__(self):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Amadeus API credentials
        self.amadeus_key = os.getenv("AMADEUS_API_KEY")
        self.amadeus_secret = os.getenv("AMADEUS_API_SECRET")
        
        # Initialize Amadeus client if credentials are available
        self.amadeus_client = None
        if self.amadeus_key and self.amadeus_secret:
            try:
                from amadeus import Client, ResponseError
                self.amadeus_client = Client(
                    client_id=self.amadeus_key,
                    client_secret=self.amadeus_secret
                )
                print("✅ Amadeus API client initialized successfully")
            except ImportError:
                print("❌ Amadeus SDK not installed. Using mock data.")
            except Exception as e:
                print(f"❌ Failed to initialize Amadeus client: {e}")
        else:
            print("⚠️  Amadeus API credentials not found. Using mock data.")
            print("   Set AMADEUS_API_KEY and AMADEUS_API_SECRET in .env file")
        
        # Booking.com backup
        self.booking_com_key = os.getenv("BOOKING_COM_API_KEY", "test_key")
        self.base_url = "https://distribution-xml.booking.com"
    
    async def search_hotels(self, params: HotelSearchParams) -> List[Dict[str, Any]]:
        """Search for hotels using Amadeus API"""
        try:
            if self.amadeus_client:
                print(f"🏨 Searching hotels in {params.destination} via Amadeus API...")
                return await self._amadeus_hotel_search(params)
            else:
                print("🏨 Using mock hotel data (Amadeus API not configured)")
                return await self._mock_hotel_search(params)
                
        except Exception as e:
            print(f"❌ Hotel search error: {e}")
            print("🏨 Falling back to mock hotel data")
            return await self._mock_hotel_search(params)
    
    async def _amadeus_hotel_search(self, params: HotelSearchParams) -> List[Dict[str, Any]]:
        """Search for hotels using Amadeus API"""
        try:
            # Get city IATA code for hotel search
            city_code = await self._get_city_code(params.destination)
            
            # Format dates for Amadeus API
            check_in_date = params.check_in.strftime("%Y-%m-%d")
            check_out_date = params.check_out.strftime("%Y-%m-%d")
            
            # Search hotels by city using Amadeus Hotel Search API
            print(f"🔍 Searching hotels in {city_code} ({params.destination})")
            print(f"📅 Check-in: {check_in_date}, Check-out: {check_out_date}")
            
            if not self.amadeus_client:
                print("⚠️  Amadeus client not available")
                return await self._mock_hotel_search(params)
                
            response = self.amadeus_client.reference_data.locations.hotels.by_city.get(
                cityCode=city_code
            )
            
            hotels = []
            if response.data:
                # Get hotel offers for the first few hotels
                for hotel_data in response.data[:5]:  # Limit to 5 hotels for performance
                    hotel_id = hotel_data['hotelId']
                    
                    try:
                        # Get hotel offers
                        if not self.amadeus_client:
                            continue
                        print(f"🏨 Getting offers for hotel {hotel_id}...")
                        offers_response = self.amadeus_client.shopping.hotel_offers_search.get(
                            hotelIds=hotel_id,
                            checkInDate=check_in_date,
                            checkOutDate=check_out_date,
                            adults=params.guests
                        )
                        
                        if offers_response.data:
                            hotel_offer = offers_response.data[0]
                            hotel_info = hotel_offer['hotel']
                            offers = hotel_offer.get('offers', [])
                            
                            if offers:
                                best_offer = offers[0]  # Take the first (usually best) offer
                                price_info = best_offer.get('price', {})
                                
                                nights = (params.check_out - params.check_in).days
                                total_price = float(price_info.get('total', 0))
                                price_per_night = total_price / nights if nights > 0 else total_price
                                
                                # Skip if over budget
                                if params.max_price_per_night and price_per_night > float(params.max_price_per_night):
                                    continue
                                
                                hotel = {
                                    "id": hotel_info.get('hotelId', f"amadeus_{hotel_id}"),
                                    "name": hotel_info.get('name', 'Unknown Hotel'),
                                    "rating": float(hotel_info.get('rating', 4.0)),
                                    "review_score": 8.0,  # Default since Amadeus doesn't provide this
                                    "total_reviews": 100,  # Default
                                    "location": hotel_info.get('cityCode', params.destination),
                                    "address": hotel_info.get('address', {}).get('lines', [''])[0] or f"{params.destination}",
                                    "price_per_night": Decimal(str(price_per_night)),
                                    "total_price": Decimal(str(total_price)),
                                    "currency": price_info.get('currency', 'USD'),
                                    "amenities": hotel_info.get('amenities', ['Free WiFi']),
                                    "room_type": best_offer.get('room', {}).get('typeEstimated', {}).get('category', 'Standard Room'),
                                    "breakfast_included": 'BREAKFAST' in str(best_offer.get('board', '')),
                                    "cancellation_policy": best_offer.get('policies', {}).get('cancellation', {}).get('description', 'See hotel policy'),
                                    "distance_to_center": "City center area",
                                    "amadeus_offer_id": best_offer.get('id')
                                }
                                hotels.append(hotel)
                                print(f"✅ Found: {hotel['name']} - ${price_per_night:.2f}/night")
                                
                    except Exception as offer_error:
                        print(f"⚠️  Could not get offers for hotel {hotel_id}: {offer_error}")
                        continue
                        
            if not hotels:
                print("ℹ️  No hotels found via Amadeus API, using mock data")
                return await self._mock_hotel_search(params)
                
            print(f"🏨 Found {len(hotels)} hotels via Amadeus API")
            return hotels
            
        except Exception as e:
            print(f"❌ Amadeus hotel search failed: {e}")
            print("🏨 Falling back to mock data")
            return await self._mock_hotel_search(params)
    
    async def _get_city_code(self, destination: str) -> str:
        """Get IATA city code for hotel search"""
        return self._fallback_city_code_resolution(destination)
    
    def _fallback_city_code_resolution(self, destination: str) -> str:
        """Fallback city code resolution using hardcoded mapping"""
        # Expanded city mappings for better coverage
        city_mapping = {
            # Major European Cities
            'paris': 'PAR',
            'london': 'LON', 
            'amsterdam': 'AMS',
            'barcelona': 'BCN',
            'rome': 'ROM',
            'madrid': 'MAD',
            'berlin': 'BER',
            'vienna': 'VIE',
            'zurich': 'ZUR',
            'geneva': 'GVA',
            'milan': 'MIL',
            'florence': 'FLR',
            'venice': 'VCE',
            'athens': 'ATH',
            'lisbon': 'LIS',
            'prague': 'PRG',
            'budapest': 'BUD',
            'warsaw': 'WAW',
            'stockholm': 'STO',
            'oslo': 'OSL',
            'copenhagen': 'CPH',
            'helsinki': 'HEL',
            'dublin': 'DUB',
            'edinburgh': 'EDI',
            'manchester': 'MAN',
            
            # North American Cities  
            'new york': 'NYC',
            'los angeles': 'LAX',
            'chicago': 'CHI',
            'miami': 'MIA',
            'las vegas': 'LAS',
            'san francisco': 'SFO',
            'boston': 'BOS',
            'washington': 'WAS',
            'seattle': 'SEA',
            'toronto': 'YTO',
            'vancouver': 'YVR',
            'montreal': 'YMQ',
            
            # Asian Cities
            'tokyo': 'TYO',
            'osaka': 'OSA',
            'kyoto': 'ITM',  # Uses Osaka airports
            'seoul': 'SEL',
            'beijing': 'BJS',
            'shanghai': 'SHA',
            'hong kong': 'HKG',
            'singapore': 'SIN',
            'bangkok': 'BKK',
            'mumbai': 'BOM',
            'delhi': 'DEL',
            'bangalore': 'BLR',
            'kuala lumpur': 'KUL',
            'jakarta': 'JKT',
            'manila': 'MNL',
            
            # Middle East & Africa
            'dubai': 'DXB',
            'doha': 'DOH',
            'abu dhabi': 'AUH',
            'istanbul': 'IST',
            'cairo': 'CAI',
            'casablanca': 'CMN',
            'johannesburg': 'JNB',
            'cape town': 'CPT',
            
            # Oceania
            'sydney': 'SYD',
            'melbourne': 'MEL',
            'brisbane': 'BNE',
            'perth': 'PER',
            'auckland': 'AKL',
            
            # South America
            'sao paulo': 'SAO',
            'rio de janeiro': 'RIO',
            'buenos aires': 'BUE',
            'lima': 'LIM',
            'santiago': 'SCL',
            'bogota': 'BOG',
            
            # Egypt & North Africa (commonly searched)
            'cairo': 'CAI',
            'alexandria': 'HBE',
            'sharm el sheikh': 'SSH',
            'hurghada': 'HRG',
            'luxor': 'LXR',
            'aswan': 'ASW',
            'marsa alam': 'RMF',
        }
        
        # Country to major city mapping for common searches
        country_to_city_mapping = {
            'egypt': 'cairo',
            'france': 'paris',
            'uk': 'london',
            'united kingdom': 'london',
            'england': 'london',
            'spain': 'madrid',
            'italy': 'rome',
            'germany': 'berlin',
            'japan': 'tokyo',
            'china': 'beijing',
            'india': 'delhi',
            'australia': 'sydney',
            'canada': 'toronto',
            'brazil': 'sao paulo',
            'argentina': 'buenos aires',
            'turkey': 'istanbul',
            'greece': 'athens',
            'portugal': 'lisbon',
            'netherlands': 'amsterdam',
            'sweden': 'stockholm',
            'norway': 'oslo',
            'denmark': 'copenhagen',
            'finland': 'helsinki',
            'russia': 'moscow',
            'south korea': 'seoul',
            'thailand': 'bangkok',
            'singapore': 'singapore',
            'malaysia': 'kuala lumpur',
            'indonesia': 'jakarta',
            'philippines': 'manila',
            'vietnam': 'ho chi minh city',
            'south africa': 'johannesburg',
            'morocco': 'casablanca',
            'uae': 'dubai',
            'united arab emirates': 'dubai',
        }
        
        # Clean destination and look up
        clean_dest = destination.lower().strip()
        original_dest = clean_dest
        
        # Remove common suffixes like "france", "uk", "usa", etc.
        clean_dest = clean_dest.replace(', france', '').replace(', uk', '').replace(', usa', '')
        clean_dest = clean_dest.replace(' france', '').replace(' uk', '').replace(' usa', '')
        clean_dest = clean_dest.replace(', united kingdom', '').replace(', united states', '')
        clean_dest = clean_dest.replace(', japan', '').replace(', germany', '').replace(', italy', '')
        clean_dest = clean_dest.replace(', spain', '').replace(', netherlands', '').strip()
        
        # Check if this looks like a country name first
        if clean_dest in country_to_city_mapping:
            major_city = country_to_city_mapping[clean_dest]
            if major_city in city_mapping:
                code = city_mapping[major_city]
                print(f"🌍 Country '{clean_dest}' mapped to major city '{major_city}' → {code}")
                return code
        
        # Also check original destination for country patterns
        if original_dest in country_to_city_mapping:
            major_city = country_to_city_mapping[original_dest]
            if major_city in city_mapping:
                code = city_mapping[major_city]
                print(f"🌍 Country '{original_dest}' mapped to major city '{major_city}' → {code}")
                return code
        
        # Try exact match first
        if clean_dest in city_mapping:
            code = city_mapping[clean_dest]
            print(f"✅ Found exact match: '{clean_dest}' → {code}")
            return code
            
        # Try partial match
        for city, code in city_mapping.items():
            if city in clean_dest or clean_dest in city:
                print(f"✅ Found partial match: '{clean_dest}' contains '{city}' → {code}")
                return code
                
        # If not found in mapping, try to get from Amadeus Location API
        if self.amadeus_client:
            print(f"🔍 Searching Amadeus Location API for: '{destination}'")
            try:
                response = self.amadeus_client.reference_data.locations.get(
                    keyword=destination.strip(),
                    subType='CITY',
                    page={'limit': 5}
                )
                if response.data and len(response.data) > 0:
                    best_match = response.data[0]
                    city_code = best_match.get('iataCode')
                    city_name = best_match.get('name', 'Unknown')
                    print(f"✅ Amadeus API found: '{city_name}' → {city_code}")
                    return city_code
                else:
                    print(f"❌ No results from Amadeus Location API for '{destination}'")
            except Exception as e:
                print(f"❌ Amadeus Location API error for '{destination}': {e}")
                
            # Try a simpler keyword search if the full destination failed
            simple_keyword = clean_dest.split(',')[0].split(' ')[0].strip()
            if simple_keyword != clean_dest and len(simple_keyword) > 2:
                print(f"🔄 Trying simplified search with: '{simple_keyword}'")
                try:
                    response = self.amadeus_client.reference_data.locations.get(
                        keyword=simple_keyword,
                        subType='CITY',
                        page={'limit': 3}
                    )
                    if response.data and len(response.data) > 0:
                        best_match = response.data[0]
                        city_code = best_match.get('iataCode')
                        city_name = best_match.get('name', 'Unknown')
                        print(f"✅ Simplified search found: '{city_name}' → {city_code}")
                        return city_code
                except Exception as e:
                    print(f"❌ Simplified search failed: {e}")
            
        # Final fallback - use first 3 letters of destination as city code
        fallback_code = clean_dest[:3].upper()
        print(f"⚠️  Using fallback city code for '{destination}': {fallback_code}")
        return fallback_code
    
    async def _mock_hotel_search(self, params: HotelSearchParams) -> List[Dict[str, Any]]:
        """Mock hotel search results for development"""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        nights = (params.check_out - params.check_in).days
        max_price = params.max_price_per_night or Decimal("200")
        
        return [
            {
                "id": "hotel_001",
                "name": "Grand City Hotel",
                "rating": 4.5,
                "review_score": 8.7,
                "total_reviews": 2847,
                "location": "City Center",
                "address": f"123 Main St, {params.destination}",
                "price_per_night": max_price * Decimal("0.8"),
                "total_price": max_price * Decimal("0.8") * nights,
                "currency": "USD",
                "amenities": ["Free WiFi", "Pool", "Fitness Center", "Restaurant", "Room Service"],
                "room_type": "Deluxe Double Room",
                "breakfast_included": True,
                "cancellation_policy": "Free cancellation until 24 hours before check-in",
                "distance_to_center": "0.2 km"
            },
            {
                "id": "hotel_002",
                "name": "Budget Inn Express",
                "rating": 3.8,
                "review_score": 7.9,
                "total_reviews": 1523,
                "location": "Near Airport",
                "address": f"456 Airport Rd, {params.destination}",
                "price_per_night": max_price * Decimal("0.5"),
                "total_price": max_price * Decimal("0.5") * nights,
                "currency": "USD",
                "amenities": ["Free WiFi", "Parking", "24h Reception"],
                "room_type": "Standard Double Room",
                "breakfast_included": False,
                "cancellation_policy": "Free cancellation until 48 hours before check-in",
                "distance_to_center": "8.5 km"
            },
            {
                "id": "hotel_003",
                "name": "Luxury Resort & Spa",
                "rating": 5.0,
                "review_score": 9.2,
                "total_reviews": 892,
                "location": "Beachfront",
                "address": f"789 Ocean View Ave, {params.destination}",
                "price_per_night": max_price * Decimal("1.5"),
                "total_price": max_price * Decimal("1.5") * nights,
                "currency": "USD", 
                "amenities": ["Private Beach", "Spa", "Multiple Restaurants", "Pool", "Concierge", "Room Service"],
                "room_type": "Ocean View Suite",
                "breakfast_included": True,
                "cancellation_policy": "Free cancellation until 7 days before check-in",
                "distance_to_center": "12.3 km"
            }
        ]


class ActivityBookingAPI:
    """Integration with TripAdvisor and other activity booking APIs"""
    
    def __init__(self):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # TripAdvisor API configuration
        self.tripadvisor_key = os.getenv("TRIPADVISOR_API_KEY")
        self.tripadvisor_base_url = "https://api.content.tripadvisor.com/api/v1"
        
        # Other API keys
        self.getyourguide_key = os.getenv("GETYOURGUIDE_API_KEY", "test_key")
        self.viator_key = os.getenv("VIATOR_API_KEY", "test_key")
        
        if self.tripadvisor_key:
            print("✅ TripAdvisor API key configured successfully")
        else:
            print("⚠️  TripAdvisor API key not found. Using mock data.")
            print("   Set TRIPADVISOR_API_KEY in .env file")
    
    async def search_activities(self, destination: str, max_budget: Decimal, preferences: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for activities and attractions using TripAdvisor API"""
        try:
            if self.tripadvisor_key:
                print(f"🎯 Searching activities in {destination} via TripAdvisor API...")
                return await self._tripadvisor_activity_search(destination, max_budget, preferences or [])
            else:
                print("🎯 Using mock activity data (TripAdvisor API not configured)")
                return await self._mock_activity_search(destination, max_budget, preferences or [])
                
        except Exception as e:
            print(f"❌ Activity search error: {e}")
            print("🎯 Falling back to mock activity data")
            return await self._mock_activity_search(destination, max_budget, preferences or [])

    async def _tripadvisor_activity_search(self, destination: str, max_budget: Decimal, preferences: List[str]) -> List[Dict[str, Any]]:
        """Search TripAdvisor for diverse local attractions, sights to see, and experiences to do"""
        try:
            headers = {
                "accept": "application/json",
                "X-RapidAPI-Key": self.tripadvisor_key,
                "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com"
            }
            
            # Enhanced search strategies for both SIGHTS TO SEE and THINGS TO DO
            search_queries = [
                # SIGHTS TO SEE (Tourist Attractions)
                f"tourist attractions {destination}",
                f"landmarks {destination}", 
                f"monuments {destination}",
                f"sightseeing {destination}",
                f"historic sites {destination}",
                f"viewpoints {destination}",
                
                # THINGS TO DO (Activities & Experiences) 
                f"activities {destination}",
                f"museums {destination}",
                f"entertainment {destination}",
                f"cultural experiences {destination}",
                f"tours {destination}",
                f"things to do {destination}"
            ]
            
            all_activities = []
            
            print(f"🔍 Searching TripAdvisor for diverse activities in: {destination}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                for search_query in search_queries[:3]:  # Try first 3 queries to avoid timeout
                    try:
                        # Step 1: Search for location ID 
                        location_url = "https://tripadvisor16.p.rapidapi.com/api/v1/attraction/searchLocation"
                        location_params = {"query": search_query}
                        
                        location_response = await client.get(location_url, headers=headers, params=location_params)
                        location_data = location_response.json()
                        
                        if not location_data.get("data"):
                            continue
                        
                        location_id = location_data["data"][0]["locationId"]
                        
                        # Step 2: Get attractions for this location/query
                        attractions_url = "https://tripadvisor16.p.rapidapi.com/api/v1/attraction/searchAttractions" 
                        attractions_params = {"locationId": location_id}
                        
                        attractions_response = await client.get(attractions_url, headers=headers, params=attractions_params)
                        attractions_data = attractions_response.json()
                        
                        if attractions_data.get("data", {}).get("data"):
                            for attraction in attractions_data["data"]["data"][:4]:  # Limit per query
                                activity = self._process_tripadvisor_attraction(attraction, destination, max_budget)
                                if activity is not None and activity not in all_activities:
                                    all_activities.append(activity)
                                    
                    except Exception as query_error:
                        print(f"⚠️  Search query '{search_query}' failed: {query_error}")
                        continue
                
                # Remove duplicates and filter diverse activity types
                unique_activities = self._filter_diverse_activities(all_activities, max_budget)
                
                if unique_activities:
                    # Enhance images with Google Places API, especially for Egypt
                    enhanced_activities = await self._enhance_with_google_places_images(unique_activities, destination)
                    print(f"✅ Found {len(enhanced_activities)} diverse TripAdvisor activities")
                    return enhanced_activities[:8]  # Return top 8 diverse activities
                else:
                    print(f"⚠️  No diverse activities found, using enhanced mock data")
                    return await self._mock_activity_search(destination, max_budget, preferences)
                
                attractions_response = await client.get(attractions_url, headers=headers, params=attractions_params)
                attractions_data = attractions_response.json()
                
                activities = []
                if attractions_data.get("data", {}).get("data"):
                    for attraction in attractions_data["data"]["data"][:8]:  # Limit to 8 activities
                        # Generate realistic pricing based on activity type and budget
                        base_price = float(max_budget) * 0.15  # 15% of budget per activity
                        price_variation = base_price * 0.5  # ±50% variation
                        price = max(10, base_price + (hash(attraction.get("name", "")) % 100 - 50) / 100 * price_variation)
                        
                        activity = {
                            "name": attraction.get("name", "Unknown Activity"),
                            "type": attraction.get("primaryInfo", "Attraction"),
                            "description": attraction.get("secondaryInfo", "Popular local attraction"),
                            "location": destination,
                            "price": round(price, 2),
                            "duration": self._estimate_duration(attraction.get("primaryInfo", "")),
                            "rating": float(attraction.get("averageRating", 4.0)),
                            "image_url": attraction.get("cardPhoto", {}).get("sizes", {}).get("urlTemplate", "").replace("{width}", "300").replace("{height}", "200") if attraction.get("cardPhoto") else None,
                            "tripadvisor_url": f"https://www.tripadvisor.com{attraction.get('detailsV2', {}).get('url', '')}" if attraction.get('detailsV2') else None,
                            "source": "tripadvisor"
                        }
                        
                        # Filter by budget
                        if activity["price"] <= float(max_budget):
                            activities.append(activity)
                
                print(f"✅ Found {len(activities)} TripAdvisor activities within budget")
                return activities[:6]  # Return top 6 activities
                
        except Exception as e:
            print(f"❌ TripAdvisor API error: {e}")
            return await self._mock_activity_search(destination, max_budget, preferences)

    def _process_tripadvisor_attraction(self, attraction: dict, destination: str, max_budget: Decimal) -> Optional[dict]:
        """Process a TripAdvisor attraction into our activity format"""
        # Generate realistic pricing based on activity type and budget
        base_price = float(max_budget) * 0.12  # 12% of budget per activity
        price_variation = base_price * 0.6  # ±60% variation
        price = max(15, base_price + (hash(attraction.get("name", "")) % 100 - 50) / 100 * price_variation)
        
        # Categorize activity type more specifically
        primary_info = attraction.get("primaryInfo", "").lower()
        activity_type = self._categorize_activity_type(primary_info)
        
        # Get image URL - prefer Google Places for better quality, especially for Egypt
        image_url = self._get_attraction_image_url(attraction)
        activity_name = attraction.get("name", "Unknown Activity")
        
        activity = {
            "name": activity_name,
            "type": activity_type,
            "description": attraction.get("secondaryInfo", "Interesting local experience"),
            "location": destination,
            "price": round(price, 2),
            "duration": self._estimate_duration(primary_info),
            "rating": float(attraction.get("averageRating", 4.2)),
            "image_url": image_url,
            "tripadvisor_url": self._get_attraction_url(attraction),
            "source": "tripadvisor",
            "category": primary_info,
            "google_places_image_pending": True,  # Flag to fetch Google Places image later
            "activity_name_for_google": activity_name  # Store for Google Places search
        }
        
        if activity["price"] <= float(max_budget):
            return activity
        return None

    def _categorize_activity_type(self, primary_info: str) -> str:
        """Categorize into sights to see vs activities to do for better diversity"""
        # SIGHTS TO SEE (Tourist Attractions)
        if any(word in primary_info for word in ["landmark", "monument", "statue", "memorial"]):
            return "landmark_sight"
        elif any(word in primary_info for word in ["viewpoint", "observation", "overlook", "scenic"]):
            return "viewpoint_sight"  
        elif any(word in primary_info for word in ["palace", "castle", "fortress", "citadel"]):
            return "historic_sight"
        elif any(word in primary_info for word in ["bridge", "tower", "building", "architecture"]):
            return "architectural_sight"
        elif any(word in primary_info for word in ["square", "plaza", "district", "neighborhood"]):
            return "district_sight"
        
        # ACTIVITIES TO DO (Experiences)
        elif any(word in primary_info for word in ["museum", "gallery", "art", "exhibit"]):
            return "museum_activity"
        elif any(word in primary_info for word in ["park", "garden", "nature", "outdoor"]):
            return "outdoor_activity"  
        elif any(word in primary_info for word in ["church", "cathedral", "temple", "religious"]):
            return "religious_visit"
        elif any(word in primary_info for word in ["market", "shopping", "bazaar", "souk"]):
            return "shopping_experience"
        elif any(word in primary_info for word in ["restaurant", "food", "dining", "cuisine"]):
            return "dining_experience"
        elif any(word in primary_info for word in ["theater", "show", "entertainment", "music", "performance"]):
            return "entertainment_activity"
        elif any(word in primary_info for word in ["tour", "walking", "guide", "excursion"]):
            return "guided_experience"
        else:
            return "general_attraction"

    def _filter_diverse_activities(self, activities: list, max_budget: Decimal) -> list:
        """Filter activities to ensure diversity of types and avoid too many similar activities"""
        if not activities:
            return []
            
        # Group by category and select diverse ones
        category_groups = {}
        for activity in activities:
            category = activity.get("category", "other").lower()
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(activity)
        
        # Select best activity from each category (max 2 per category)
        diverse_activities = []
        for category, group in category_groups.items():
            # Sort by rating and select top activities from this category
            sorted_group = sorted(group, key=lambda x: x.get("rating", 0), reverse=True)
            diverse_activities.extend(sorted_group[:2])  # Max 2 per category
        
        # Remove activities with same or very similar names
        unique_activities = []
        seen_names = set()
        for activity in diverse_activities:
            activity_name = activity.get("name", "").lower()
            # Check if it's too similar to existing activities
            is_duplicate = any(
                activity_name in seen_name or seen_name in activity_name 
                for seen_name in seen_names
            )
            if not is_duplicate:
                unique_activities.append(activity)
                seen_names.add(activity_name)
        
        # Sort by rating and budget fit
        return sorted(unique_activities, key=lambda x: (x.get("rating", 0), -x.get("price", 0)), reverse=True)

    def _get_attraction_image_url(self, attraction: dict) -> str:
        """Extract image URL from TripAdvisor attraction data"""
        card_photo = attraction.get("cardPhoto", {})
        if card_photo and card_photo.get("sizes", {}).get("urlTemplate"):
            return card_photo["sizes"]["urlTemplate"].replace("{width}", "400").replace("{height}", "300")
        return ""
    
    async def _get_google_places_image(self, place_name: str, destination: str) -> str:
        """Get high-quality image from Google Places API"""
        try:
            google_places_key = os.getenv("GOOGLE_PLACES_API_KEY")
            if not google_places_key:
                return ""
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Search for the specific place
                search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                search_params = {
                    "query": f"{place_name} {destination}",
                    "key": google_places_key
                }
                
                response = await client.get(search_url, params=search_params)
                response.raise_for_status()
                search_data = response.json()
                
                if search_data.get("status") == "OK" and search_data.get("results"):
                    place = search_data["results"][0]
                    photos = place.get("photos", [])
                    
                    if photos:
                        photo_reference = photos[0].get("photo_reference")
                        if photo_reference:
                            # Get high-quality photo
                            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={google_places_key}"
                            return photo_url
                            
        except Exception as e:
            print(f"⚠️ Google Places image fetch error: {e}")
        
        return ""
    
    async def _enhance_with_google_places_images(self, activities: List[Dict[str, Any]], destination: str) -> List[Dict[str, Any]]:
        """Enhance activities with Google Places images, especially for Egypt and when TripAdvisor images are missing"""
        google_places_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not google_places_key:
            print("⚠️ Google Places API not configured - using TripAdvisor images only")
            return activities
        
        enhanced_activities = []
        
        for activity in activities:
            # Check if we should fetch a Google Places image
            should_fetch_google_image = (
                not activity.get("image_url") or  # No TripAdvisor image
                "egypt" in destination.lower() or  # Always enhance Egypt images
                "cairo" in destination.lower() or
                "giza" in destination.lower() or
                "luxor" in destination.lower()
            )
            
            if should_fetch_google_image and activity.get("activity_name_for_google"):
                try:
                    google_image = await self._get_google_places_image(
                        activity["activity_name_for_google"], 
                        destination
                    )
                    if google_image:
                        activity["image_url"] = google_image
                        activity["image_source"] = "google_places"
                        print(f"🖼️ Enhanced image for {activity['name']} via Google Places")
                    elif not activity.get("image_url"):
                        # Fallback to a generic travel image
                        activity["image_url"] = self._get_fallback_image_url(activity["name"], destination)
                        activity["image_source"] = "fallback"
                except Exception as e:
                    print(f"⚠️ Failed to enhance image for {activity['name']}: {e}")
            
            # Clean up temporary fields
            activity.pop("google_places_image_pending", None)
            activity.pop("activity_name_for_google", None)
            
            enhanced_activities.append(activity)
        
        return enhanced_activities
    
    def _get_fallback_image_url(self, activity_name: str, destination: str) -> str:
        """Provide fallback images for activities when APIs fail"""
        # Use Unsplash for high-quality travel images
        query = f"{destination} travel"
        if "egypt" in destination.lower():
            if any(keyword in activity_name.lower() for keyword in ["pyramid", "giza", "sphinx"]):
                query = "egypt pyramids"
            elif any(keyword in activity_name.lower() for keyword in ["nile", "river", "cruise"]):
                query = "nile river egypt"
            elif any(keyword in activity_name.lower() for keyword in ["temple", "luxor", "karnak"]):
                query = "egypt temple"
            else:
                query = "egypt cairo"
        
        return f"https://source.unsplash.com/800x600/?{query.replace(' ', ',')}"

    def _get_attraction_url(self, attraction: dict) -> str:
        """Extract TripAdvisor URL from attraction data"""
        details = attraction.get("detailsV2", {})
        if details and details.get("url"):
            return f"https://www.tripadvisor.com{details['url']}"
        return ""

    def _estimate_duration(self, activity_type: str) -> str:
        """Estimate activity duration based on type"""
        activity_type = activity_type.lower()
        if any(word in activity_type for word in ["museum", "gallery", "exhibit"]):
            return "2-3 hours"
        elif any(word in activity_type for word in ["tour", "walking", "guide"]):
            return "3-4 hours"
        elif any(word in activity_type for word in ["park", "garden", "outdoor"]):
            return "1-2 hours"
        elif any(word in activity_type for word in ["restaurant", "food", "dining"]):
            return "1-1.5 hours"
        else:
            return "2-3 hours"

    async def _mock_activity_search(self, destination: str, max_budget: Decimal, preferences: List[str]) -> List[Dict[str, Any]]:
        """Mock activity search results for development with diverse activities"""
        await asyncio.sleep(0.4)  # Simulate API delay
        
        # Enhanced activities including both SIGHTS TO SEE and THINGS TO DO
        base_activities = [
            # SIGHTS TO SEE (Tourist Attractions)
            {
                "id": "sight_001",
                "name": f"Iconic {destination} Cultural Landmark",
                "category": "landmark_sight", 
                "description": f"Visit the most famous cultural landmark in {destination} - a must-see architectural marvel and symbol of the city's heritage.",
                "duration": "1 hour",
                "price": min(max_budget * Decimal("0.08"), Decimal("15")),
                "currency": "USD",
                "rating": 4.8,
                "total_reviews": 3421,
                "highlights": ["Iconic architecture", "Photo opportunities", "Cultural significance"],
                "includes": ["Entry ticket", "Information placard", "Self-guided viewing"],
                "meeting_point": f"Main Entrance, {destination}",
                "languages": ["Multiple languages"],
                "group_size": "Individual"
            },
            {
                "id": "sight_002",
                "name": f"{destination} Scenic Viewpoint",
                "category": "viewpoint_sight",
                "description": f"Breathtaking panoramic views of {destination} from the city's best elevated viewpoint - perfect for cultural sightseeing.", 
                "duration": "1.5 hours",
                "price": min(max_budget * Decimal("0.1"), Decimal("20")),
                "currency": "USD",
                "rating": 4.9,
                "total_reviews": 2156,
                "highlights": ["360° city views", "Perfect for photos", "Cultural landmarks below"],
                "includes": ["Viewpoint access", "Observation deck", "Photo opportunities"],
                "meeting_point": f"Viewpoint Base, {destination}",
                "languages": ["English", "Local language"],
                "group_size": "Individual"
            },
            {
                "id": "sight_003", 
                "name": f"Historic {destination} Cultural District",
                "category": "district_sight",
                "description": f"Wander through the charming historic cultural district with cobblestone streets, traditional architecture, and authentic local atmosphere.",
                "duration": "2 hours",
                "price": Decimal("0"),  # Free to walk around
                "currency": "USD",
                "rating": 4.6,
                "total_reviews": 1834,
                "highlights": ["Historic architecture", "Cultural heritage", "Local atmosphere"],
                "includes": ["Self-guided exploration", "Free walking", "Photo opportunities"],
                "meeting_point": f"Old Town Square, {destination}",
                "languages": ["Self-guided"],
                "group_size": "Individual"
            },
            
            # THINGS TO DO (Activities & Experiences)
            {
                "id": "activity_001",
                "name": f"{destination} National Museum",
                "category": "museum_activity",
                "description": f"Discover {destination}'s rich history and culture at the premier national museum with world-class exhibits.",
                "duration": "3 hours",
                "price": min(max_budget * Decimal("0.15"), Decimal("25")),
                "currency": "USD",
                "rating": 4.6,
                "total_reviews": 1247,
                "highlights": ["World-class exhibits", "Interactive displays", "Audio guide included"],
                "includes": ["Museum entry", "Audio guide", "Map"],
                "meeting_point": f"Museum Main Entrance, {destination}",
                "languages": ["English", "Spanish"],
                "group_size": "Individual"
            },
            {
                "id": "activity_002",
                "name": f"Local Market Food Experience",
                "category": "dining_experience",
                "description": f"Explore the vibrant local market and taste authentic street food with a knowledgeable foodie guide.",
                "duration": "2 hours",
                "price": min(max_budget * Decimal("0.25"), Decimal("40")),
                "currency": "USD", 
                "rating": 4.7,
                "total_reviews": 634,
                "highlights": ["Authentic street food", "Local market culture", "Hidden food gems"],
                "includes": ["Food tastings", "Market tour", "Local guide"],
                "meeting_point": f"Central Market, {destination}",
                "languages": ["English", "Local language"],
                "group_size": "Max 8 people"
            },
            {
                "id": "activity_003",
                "name": f"Cultural {destination} Walking Tour", 
                "category": "guided_experience",
                "description": f"Discover local street art, galleries, and creative spaces in {destination}'s vibrant cultural district.",
                "duration": "2.5 hours",
                "price": min(max_budget * Decimal("0.2"), Decimal("30")),
                "currency": "USD",
                "rating": 4.5,
                "total_reviews": 456,
                "highlights": ["Street art murals", "Local galleries", "Artist studios"],
                "includes": ["Walking tour", "Gallery visits", "Local artist stories"],
                "meeting_point": f"Art District Plaza, {destination}",
                "languages": ["English"],
                "group_size": "Max 12 people"
            },
            
            # MORE SIGHTS TO SEE
            {
                "id": "sight_004",
                "name": f"Famous {destination} Bridge",
                "category": "architectural_sight",
                "description": f"Admire the stunning architecture of {destination}'s most famous bridge, perfect for photos and leisurely walks.",
                "duration": "45 minutes",
                "price": Decimal("0"),  # Free to visit
                "currency": "USD",
                "rating": 4.7,
                "total_reviews": 2891,
                "highlights": ["Architectural beauty", "River views", "Historic significance"],
                "includes": ["Free access", "Walking across bridge", "Photo opportunities"],
                "meeting_point": f"Bridge Entrance, {destination}",
                "languages": ["Self-guided"],
                "group_size": "Individual"
            },
            {
                "id": "sight_005",
                "name": f"{destination} Central Square",
                "category": "district_sight",
                "description": f"The heart of {destination} - a bustling square surrounded by historic buildings, cafes, and local life.",
                "duration": "1 hour",
                "price": Decimal("0"),  # Free to visit
                "currency": "USD",
                "rating": 4.5,
                "total_reviews": 1456,
                "highlights": ["Historic buildings", "Local atmosphere", "People watching"],
                "includes": ["Free access", "Self-exploration", "Surrounding cafes"],
                "meeting_point": f"Central Square, {destination}",
                "languages": ["Self-guided"],
                "group_size": "Individual"
            },
            
            # MORE ACTIVITIES TO DO
            {
                "id": "activity_004",
                "name": f"{destination} Local Craft Workshop",
                "category": "cultural_experience", 
                "description": f"Learn traditional local crafts in a hands-on workshop led by skilled artisans.",
                "duration": "3 hours",
                "price": min(max_budget * Decimal("0.18"), Decimal("35")),
                "currency": "USD",
                "rating": 4.8,
                "total_reviews": 423,
                "highlights": ["Hands-on learning", "Traditional techniques", "Take home creation"],
                "includes": ["All materials", "Expert instruction", "Finished product"],
                "meeting_point": f"Artisan Workshop, {destination}",
                "languages": ["English", "Local language"],
                "group_size": "Max 6 people"
            },
            {
                "id": "activity_005",
                "name": f"Traditional {destination} Performance",
                "category": "entertainment_activity",
                "description": f"Experience authentic local culture through traditional music and dance performances.",
                "duration": "1.5 hours",
                "price": min(max_budget * Decimal("0.22"), Decimal("35")),
                "currency": "USD",
                "rating": 4.6,
                "total_reviews": 789,
                "highlights": ["Live traditional music", "Cultural dance", "Authentic costumes"],
                "includes": ["Performance ticket", "Program booklet", "Welcome drink"],
                "meeting_point": f"Cultural Center, {destination}",
                "languages": ["English subtitles", "Local performance"],
                "group_size": "Theater seating"
            }
        ]
        
        # Filter and balance activities based on preferences - ensure mix of sights and activities
        if preferences:
            filtered_activities = []
            for activity in base_activities:
                if any(pref.lower() in activity["category"].lower() or 
                      pref.lower() in activity["name"].lower() or
                      pref.lower() in activity["description"].lower() 
                      for pref in preferences):
                    filtered_activities.append(activity)
            
            # If we have filtered results, ensure we have both sights and activities
            if filtered_activities:
                sights = [a for a in filtered_activities if "sight" in a["category"]]
                activities = [a for a in filtered_activities if "sight" not in a["category"]]
                
                # Combine for a good mix (prioritize sights if cultural preference)
                if "cultural" in [p.lower() for p in preferences]:
                    result = sights[:3] + activities[:3]  # More balance for cultural trips
                else:
                    result = sights[:2] + activities[:4]  # More activities for other preferences
                
                return result if result else base_activities[:4]
            else:
                return base_activities[:4]  # Return first 4 if no preference match
        
        # No preferences - return balanced mix of sights and activities  
        sights = [a for a in base_activities if "sight" in a["category"]]
        activities = [a for a in base_activities if "sight" not in a["category"]]
        return sights[:3] + activities[:3]


class RestaurantBookingAPI:
    """Integration with Google Places API for restaurant searches"""
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        
        self.google_places_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.google_places_base_url = "https://maps.googleapis.com/maps/api/place"
        
        if self.google_places_key:
            print("✅ Google Places API credentials detected — using real restaurant data")
        else:
            print("⚠️  Google Places API key not found. Using mock restaurant data.")
            print("   Set GOOGLE_PLACES_API_KEY in .env file")
    
    async def search_restaurants(self, destination: str, max_budget_per_meal: float = 50.0,
                               cuisine_preferences: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search for restaurants in destination using Google Places API"""
        
        if not self.google_places_key:
            print("🍽️ Using mock restaurant data (Google Places API not configured)")
            return await self._get_mock_restaurants(destination, max_budget_per_meal, cuisine_preferences)
        
        try:
            # Build search query based on preferences
            query_parts = [f"restaurants in {destination}"]
            
            if cuisine_preferences:
                # Filter preferences for cuisine-related terms
                cuisine_terms = []
                for pref in cuisine_preferences:
                    if any(cuisine in pref.lower() for cuisine in ["food", "culinary", "cuisine", "dining"]):
                        if "luxury" in pref.lower():
                            cuisine_terms.append("fine dining")
                        elif "budget" in pref.lower():
                            cuisine_terms.append("casual dining")
                        else:
                            cuisine_terms.append("restaurant")
                
                if cuisine_terms:
                    query_parts.extend(cuisine_terms)
            
            search_query = " ".join(query_parts)
            
            # Use Google Places Text Search API
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Text search for restaurants
                text_search_url = f"{self.google_places_base_url}/textsearch/json"
                text_params = {
                    "query": search_query,
                    "type": "restaurant", 
                    "key": self.google_places_key
                }
                
                response = await client.get(text_search_url, params=text_params)
                response.raise_for_status()
                search_data = response.json()
                
                restaurants = []
                if search_data.get("status") == "OK" and search_data.get("results"):
                    for place in search_data["results"][:6]:  # Get top 6 restaurants
                        # Get detailed information for each restaurant
                        place_id = place.get("place_id")
                        if place_id:
                            details = await self._get_place_details(client, place_id)
                            restaurant_info = self._parse_restaurant_data(place, details, max_budget_per_meal)
                            if restaurant_info:
                                restaurants.append(restaurant_info)
                
                if restaurants:
                    print(f"🍽️ Found {len(restaurants)} restaurants via Google Places API")
                    return {"restaurants": restaurants}
                else:
                    print("🍽️ No restaurants found via API, using mock data")
                    return await self._get_mock_restaurants(destination, max_budget_per_meal, cuisine_preferences)
                    
        except Exception as e:
            print(f"❌ Google Places API error: {e}")
            return await self._get_mock_restaurants(destination, max_budget_per_meal, cuisine_preferences)
    
    async def _get_place_details(self, client: httpx.AsyncClient, place_id: str) -> Dict[str, Any]:
        """Get detailed information about a restaurant"""
        try:
            details_url = f"{self.google_places_base_url}/details/json"
            details_params = {
                "place_id": place_id,
                "fields": "name,rating,price_level,formatted_address,formatted_phone_number,website,opening_hours,user_ratings_total,types",
                "key": self.google_places_key
            }
            
            response = await client.get(details_url, params=details_params)
            response.raise_for_status()
            details_data = response.json()
            
            if details_data.get("status") == "OK":
                return details_data.get("result", {})
        except Exception as e:
            print(f"❌ Error getting place details: {e}")
        
        return {}
    
    def _parse_restaurant_data(self, place: Dict[str, Any], details: Dict[str, Any], max_budget: float) -> Optional[Dict[str, Any]]:
        """Parse restaurant data from Google Places API response"""
        try:
            name = place.get("name", "Restaurant")
            rating = place.get("rating", 4.0)
            price_level = place.get("price_level", 2)  # 0-4 scale
            
            # Estimate cost based on price level
            price_multipliers = {0: 0.5, 1: 0.7, 2: 1.0, 3: 1.5, 4: 2.0}
            base_cost = max_budget * price_multipliers.get(price_level, 1.0)
            
            # Skip if too expensive
            if base_cost > max_budget * 1.5:
                return None
            
            # Extract cuisine types from place types
            cuisine_types = []
            place_types = place.get("types", []) + details.get("types", [])
            cuisine_keywords = ["restaurant", "food", "meal_takeaway", "cafe", "bar"]
            for place_type in place_types:
                if any(keyword in place_type.lower() for keyword in cuisine_keywords):
                    cuisine_types.append(place_type.replace("_", " ").title())
            
            if not cuisine_types:
                cuisine_types = ["Restaurant"]
            
            # Get opening hours
            opening_hours = []
            if details.get("opening_hours", {}).get("weekday_text"):
                opening_hours = details["opening_hours"]["weekday_text"][:3]  # First 3 days
            
            return {
                "id": place.get("place_id", f"restaurant_{hash(name)}"),
                "name": name,
                "rating": rating,
                "price_level": price_level,
                "address": details.get("formatted_address", place.get("vicinity", "City Center")),
                "cuisine_types": cuisine_types[:2],  # Limit to 2 types
                "estimated_cost": base_cost,
                "reviews_count": place.get("user_ratings_total", details.get("user_ratings_total", 0)),
                "phone": details.get("formatted_phone_number", ""),
                "website": details.get("website", ""),
                "opening_hours": opening_hours,
                "specialties": [f"{name} specialties", "Local favorites"] if rating >= 4.0 else ["Popular dishes"]
            }
            
        except Exception as e:
            print(f"❌ Error parsing restaurant data: {e}")
            return None
    
    async def _get_mock_restaurants(self, destination: str, max_budget: float, 
                                  cuisine_preferences: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Generate mock restaurant data as fallback"""
        
        restaurants = [
            {
                "id": "mock_rest_001",
                "name": f"{destination} Local Kitchen",
                "rating": 4.5,
                "price_level": 2,
                "address": f"123 Main Street, {destination}",
                "cuisine_types": ["Local", "Traditional"],
                "estimated_cost": max_budget * 0.8,
                "reviews_count": 250,
                "phone": "+1-555-0123",
                "website": "",
                "opening_hours": ["Mon-Sun: 11:00 AM - 10:00 PM"],
                "specialties": ["Local specialties", "Traditional dishes"]
            },
            {
                "id": "mock_rest_002", 
                "name": f"{destination} Fine Dining",
                "rating": 4.8,
                "price_level": 3,
                "address": f"456 Gourmet Avenue, {destination}",
                "cuisine_types": ["International", "Fine Dining"],
                "estimated_cost": max_budget * 1.3,
                "reviews_count": 150,
                "phone": "+1-555-0456",
                "website": "",
                "opening_hours": ["Tue-Sat: 6:00 PM - 11:00 PM"],
                "specialties": ["Chef's special", "Wine pairing"]
            },
            {
                "id": "mock_rest_003",
                "name": f"Cozy {destination} Cafe",
                "rating": 4.3,
                "price_level": 1,
                "address": f"789 Cafe Street, {destination}",
                "cuisine_types": ["Cafe", "Light Meals"],
                "estimated_cost": max_budget * 0.6,
                "reviews_count": 180,
                "phone": "+1-555-0789",
                "website": "",
                "opening_hours": ["Daily: 7:00 AM - 9:00 PM"],
                "specialties": ["Fresh pastries", "Coffee blends"]
            },
            {
                "id": "mock_rest_004",
                "name": f"{destination} Street Food Market",
                "rating": 4.2,
                "price_level": 1,
                "address": f"Central Market, {destination}",
                "cuisine_types": ["Street Food", "Casual"],
                "estimated_cost": max_budget * 0.4,
                "reviews_count": 320,
                "phone": "",
                "website": "",
                "opening_hours": ["Mon-Sat: 10:00 AM - 8:00 PM"],
                "specialties": ["Local street food", "Quick bites"]
            }
        ]
        
        return {"restaurants": restaurants}


class TravelAPIManager:
    """Main manager for all travel API integrations"""
    
    def __init__(self):
        self.flight_api = FlightBookingAPI()
        self.hotel_api = HotelBookingAPI()
        self.activity_api = ActivityBookingAPI()
        self.restaurant_api = RestaurantBookingAPI()  # ← NEW
    
    async def search_restaurants(self, destination: str, max_budget_per_meal: float = 50.0,
                               cuisine_preferences: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search for restaurants using the restaurant API"""
        return await self.restaurant_api.search_restaurants(destination, max_budget_per_meal, cuisine_preferences)
    
    async def search_all(self, destination: str, departure_location: str, 
                        start_date: date, end_date: date, 
                        travelers: int, budget: Decimal,
                        preferences: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search flights, hotels, activities, and restaurants simultaneously"""
        
        # Calculate budget allocation (updated with restaurants)
        flight_budget = budget * Decimal("0.35")   # 35% for flights (was 40%)
        hotel_budget = budget * Decimal("0.35")    # 35% for hotels  
        activity_budget = budget * Decimal("0.15") # 15% for activities (was 20%)
        restaurant_budget = budget * Decimal("0.10") # 10% for restaurants (NEW)
        # 5% buffer remaining
        
        # Create search parameters
        flight_params = FlightSearchParams(
            origin=departure_location,
            destination=destination,
            departure_date=start_date,
            return_date=end_date,
            passengers=travelers,
            max_price=flight_budget
        )
        
        nights = (end_date - start_date).days
        hotel_params = HotelSearchParams(
            destination=destination,
            check_in=start_date,
            check_out=end_date,
            guests=travelers,
            max_price_per_night=hotel_budget / nights if nights > 0 else hotel_budget
        )
        
        # Calculate restaurant budget per meal (assuming 3 meals per day)
        trip_days = (end_date - start_date).days or 1
        total_meals = trip_days * 3  # 3 meals per day
        budget_per_meal = float(restaurant_budget / total_meals) if total_meals > 0 else 50.0
        
        # Execute searches concurrently
        results = await asyncio.gather(
            self.flight_api.search_flights(flight_params),
            self.hotel_api.search_hotels(hotel_params),
            self.activity_api.search_activities(destination, activity_budget, preferences),
            self.restaurant_api.search_restaurants(destination, budget_per_meal, preferences),
            return_exceptions=True
        )
        
        # Handle results with proper typing
        flights = cast(List[Dict[str, Any]], results[0] if not isinstance(results[0], Exception) else [])
        hotels = cast(List[Dict[str, Any]], results[1] if not isinstance(results[1], Exception) else [])
        activities = cast(List[Dict[str, Any]], results[2] if not isinstance(results[2], Exception) else [])
        restaurants = cast(Dict[str, List[Dict[str, Any]]], results[3] if not isinstance(results[3], Exception) else {}).get("restaurants", [])
        
        return {
            "flights": flights,
            "hotels": hotels, 
            "activities": activities,
            "restaurants": restaurants
        }


# Export the main API manager
travel_apis = TravelAPIManager()
