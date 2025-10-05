from datetime import datetime, timedelta, timezone
from math import radians,cos,sin,asin,sqrt
from typing import Optional

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula
    Returns distance in kilometers
    """
    lon1,lat1,lon2,lat2 = map(radians, [lon1,lat1,lon2,lat2])

    #Haversine formula
    dlon= lon2-lon1
    dlat = lat2-lat1
    a = sin(dlat/2)**2 + cos(lat1)* cos(lat2)*sin(dlon/2)**2
    c= 2* asin(sqrt(a))

    #radius of earth in km
    km = 6371 * c
    return round(km , 2)

def calculate_eta_minutes(distance_km:float,average_speed_kmh:float= 30) -> int:
    """
    Calculate ETA in minutes based on distance and average speed
    Default speed: 30km/h (typical city traffic)
    """
    if distance_km <= 0 or average_speed_kmh <= 0:
        return 0
    hours = distance_km / average_speed_kmh
    minutes = int(hours * 60)
    return minutes

def format_time_ago(dt:datetime) -> str:
    """
    Format datetime as human-readable time ago
    Examples: "2 minutes ago" , "1 hour ago" , "just now"
    """
    now = datetime.now(timezone.utc)
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds/60)
        return f"{minutes} minute{"s" if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''}ago"
    
def format_duration(minutes: int) -> str:
    """
    Convert minutes to human readable duration
    Examples: "5minutes", "1 hour 30 minutes", "2 hours"
    """
    if minutes < 1:
        return "less than a minutes"
    elif minutes == 1:
        return "1 minute"
    elif minutes < 60:
        return f"{minutes} minutes"
    else:
        hours = minutes // 60
        mins = minutes % 60

        if mins == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours}h {mins}m"
        
def format_capacity(current:int, total: int) -> str:
    """
    Format bus capacity as readable string
    Example: "25/50 (50% full)"
    """
    percentage = int((current / total) * 100) if total > 0 else 0
    return f"{current}/{total} ({percentage}% full)"

def is_within_terminal(bus_lat: float, bus_lon: float, terminal_lat: float , terminal_lon: float, radius_meters: float= 100) -> bool:
    """
    check if bus is within terminal radius
    """
    distance_km = calculate_distance(bus_lat, bus_lon, terminal_lat, terminal_lon)
    distance_meters = distance_km * 1000
    return distance_meters <= radius_meters

def generate_shift_summary(shift_start: datetime, shift_end:Optional[datetime] = None) -> dict:
    """
    Generate summary of a shift
    """
    if shift_end is None:
        shift_end = datetime.now(timezone.utc)
    duration = shift_end - shift_start
    hours = duration.total_seconds() / 3600
    return {
        "start_time": shift_start.isoformat(),
        "end_time": shift_end.isoformat() if shift_end else None,
        "duration_hours": round(hours, 2),
        "duration_formatted": format_duration(int(hours * 60)),
        "is_active": shift_end is None
    }
