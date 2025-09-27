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

                for i, offer in enumerate(offers[:5]):
                    try:
                        itineraries = offer.get("itineraries", [])
                        if not itineraries:
                            continue
                        first_itin = itineraries[0]
                        segments = first_itin.get("segments", [])
                        if not segments:
                            continue
                        first_seg = segments[0]

                        carrier = first_seg.get("carrierCode", "")
                        airline = self._get_airline_name_from_code(carrier)

                        price_obj = offer.get("price", {})
                        total_price = float(price_obj.get("total", 0) or 0)

                        departure = first_seg.get("departure", {})
                        arrival = first_seg.get("arrival", {})

                        # Attempt to glean aircraft and travel class from segments/offer
                        aircraft = first_seg.get('aircraft', {}).get('code') if isinstance(first_seg.get('aircraft', {}), dict) else first_seg.get('aircraft')
                        travel_class = offer.get('travelerPricings', [{}])[0].get('fareDetailsBySegment', [{}])[0].get('cabin', '') if offer.get('travelerPricings') else ''
                        available_seats = offer.get('numberOfBookableSeats', None) or first_seg.get('numberOfBookableSeats', None)

                        flight_info = {
                            "id": f"amadeus_{i+1}",
                            "airline": airline,
                            "flight_number": f"{carrier}{first_seg.get('number', '')}",
                            "aircraft": aircraft,
                            "departure_time": departure.get("at", "") ,
                            "arrival_time": arrival.get("at", ""),
                            "departure_airport": departure.get('iataCode', origin_code),
                            "arrival_airport": arrival.get('iataCode', dest_code),
                            "duration": first_itin.get("duration", ""),
                            "price": total_price,
                            "currency": price_obj.get("currency", "USD"),
                            "stops": max(0, len(segments) - 1),
                            "class": travel_class or offer.get('class', 'Economy'),
                            "available_seats": available_seats or 0,
                            "instant_confirmation": True,
                            "source": "amadeus_api"
                        }

                        if not params.max_price or flight_info["price"] <= float(params.max_price):
                            flights.append(flight_info)
                    except Exception as item_err:
                        print(f"⚠️  Error parsing Amadeus offer: {item_err}")
                        continue

                if flights:
                    print(f"✅ Found {len(flights)} flights via Amadeus")
                    return flights
                else:
                    print("⚠️  No offers from Amadeus, falling back to mock flights")
                    return await self._mock_flight_search(params)

        except Exception as e:
            print(f"❌ Error during Amadeus flight search: {e}")
            return await self._mock_flight_search(params)

    async def _mock_flight_search(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """Mock flight search results for development"""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        base_price = min(params.max_price or Decimal("800"), Decimal("600"))
        
        return [
            {
                "id": "flight_001",
                "airline": "American Airlines",
                "flight_number": "AA1234",
                "departure_airport": self._get_airport_code(params.origin),
                "departure_airport_name": self._get_airport_name(params.origin),
                "arrival_airport": self._get_airport_code(params.destination),
                "arrival_airport_name": self._get_airport_name(params.destination),
                "departure_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=8)),
                "arrival_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=14, minute=30)),
                "duration": "6h 30m",
                "stops": 0,
                "price": base_price * Decimal("0.9"),
                "currency": "USD",
                "class": "Economy",
                "available_seats": 15,
                "aircraft": "Boeing 737-800"
            },
            {
                "id": "flight_002", 
                "airline": "Delta Air Lines",
                "flight_number": "DL5678",
                "departure_airport": self._get_airport_code(params.origin),
                "departure_airport_name": self._get_airport_name(params.origin),
                "arrival_airport": self._get_airport_code(params.destination),
                "arrival_airport_name": self._get_airport_name(params.destination),
                "departure_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=12)),
                "arrival_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=20, minute=45)),
                "duration": "8h 45m",
                "stops": 1,
                "price": base_price * Decimal("0.75"),
                "currency": "USD",
                "class": "Economy",
                "available_seats": 8,
                "aircraft": "Airbus A320"
            },
            {
                "id": "flight_003",
                "airline": "United Airlines", 
                "flight_number": "UA9012",
                "departure_airport": self._get_airport_code(params.origin),
                "departure_airport_name": self._get_airport_name(params.origin),
                "arrival_airport": self._get_airport_code(params.destination),
                "arrival_airport_name": self._get_airport_name(params.destination),
                "departure_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=15)),
                "arrival_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=21, minute=15)),
                "duration": "6h 15m",
                "stops": 0,
                "price": base_price * Decimal("1.1"),
                "currency": "USD", 
                "class": "Economy Plus",
                "available_seats": 22,
                "aircraft": "Boeing 777-300ER"
            }
        ]


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
                    print(f"✅ Found {len(unique_activities)} diverse TripAdvisor activities")
                    return unique_activities[:8]  # Return top 8 diverse activities
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
        
        activity = {
            "name": attraction.get("name", "Unknown Activity"),
            "type": activity_type,
            "description": attraction.get("secondaryInfo", "Interesting local experience"),
            "location": destination,
            "price": round(price, 2),
            "duration": self._estimate_duration(primary_info),
            "rating": float(attraction.get("averageRating", 4.2)),
            "image_url": self._get_attraction_image_url(attraction),
            "tripadvisor_url": self._get_attraction_url(attraction),
            "source": "tripadvisor",
            "category": primary_info
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


class TravelAPIManager:
    """Main manager for all travel API integrations"""
    
    def __init__(self):
        self.flight_api = FlightBookingAPI()
        self.hotel_api = HotelBookingAPI()
        self.activity_api = ActivityBookingAPI()
    
    async def search_all(self, destination: str, departure_location: str, 
                        start_date: date, end_date: date, 
                        travelers: int, budget: Decimal,
                        preferences: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search flights, hotels, and activities simultaneously"""
        
        # Calculate budget allocation
        flight_budget = budget * Decimal("0.4")  # 40% for flights
        hotel_budget = budget * Decimal("0.35")   # 35% for hotels  
        activity_budget = budget * Decimal("0.2") # 20% for activities (5% buffer)
        
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
        
        # Execute searches concurrently
        results = await asyncio.gather(
            self.flight_api.search_flights(flight_params),
            self.hotel_api.search_hotels(hotel_params),
            self.activity_api.search_activities(destination, activity_budget, preferences),
            return_exceptions=True
        )
        
        # Handle results with proper typing
        flights = cast(List[Dict[str, Any]], results[0] if not isinstance(results[0], Exception) else [])
        hotels = cast(List[Dict[str, Any]], results[1] if not isinstance(results[1], Exception) else [])
        activities = cast(List[Dict[str, Any]], results[2] if not isinstance(results[2], Exception) else [])
        
        return {
            "flights": flights,
            "hotels": hotels, 
            "activities": activities
        }


# Export the main API manager
travel_apis = TravelAPIManager()
