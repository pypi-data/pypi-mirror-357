from datetime import datetime, timezone
from zoneinfo import available_timezones, ZoneInfo, ZoneInfoNotFoundError
import logging

import dateutil
import dateutil.parser
from dateutil import tz
from mcp.server.fastmcp import FastMCP


logger = logging.getLogger(__name__)

TZINFOS = {
    "CST": tz.tzoffset("CST", -6 * 3600),  # Central Standard Time
    "CDT": tz.tzoffset("CDT", -5 * 3600),  # Central Daylight Time
    "EST": tz.tzoffset("EST", -5 * 3600),  # Eastern Standard Time
    "EDT": tz.tzoffset("EDT", -4 * 3600),  # Eastern Daylight Time
    "MST": tz.tzoffset("MST", -7 * 3600),  # Mountain Standard Time
    "MDT": tz.tzoffset("MDT", -6 * 3600),  # Mountain Daylight Time
    "PST": tz.tzoffset("PST", -8 * 3600),  # Pacific Standard Time
    "PDT": tz.tzoffset("PDT", -7 * 3600),  # Pacific Daylight Time
}


def parse_date_str_to_utc(date_str: str) -> datetime:
    """
    Parses a date string into a datetime object. If the date string does not contain a timezone,
    it will be considered as UTC. The function uses dateutil.parser to handle various date formats.
    The result well be in UTC timezone.
    :param date_str: The date string to parse.
    :return: A datetime object with timezone information.
    """
    try:
        dt = dateutil.parser.parse(date_str, tzinfos=TZINFOS)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except dateutil.parser.ParserError as e:
        logger.error("Error parsing date string: %s", e)
        raise ValueError(f"Invalid date format: '{date_str}'") from e


class DateTimeMCPTools:
    """
    A class with model context protocols (MCP) tools to handle date and time manipulations.
    """
    def register_tools(self, server: FastMCP):
        """
        Register the tools with the given name.
        """
        server.add_tool(self.get_current_datetime)
        server.add_tool(self.convert_datetime_to_utc)
        server.add_tool(self.convert_datetime_to_local_timezone)
        server.add_tool(self.convert_datetime_to_timezone)
        server.add_tool(self.get_possible_datetime_timezones)

    @staticmethod
    def get_current_datetime() -> str:
        """
        Returns the current date and time in ISO format and UTC timezone.
        """
        result = datetime.now(timezone.utc).isoformat()
        logger.info("Getting current datetime %s in UTC timezone", result)
        return result
    
    @staticmethod
    def convert_datetime_to_utc(date_str: str):
        """
        Converts a date string to UTC timezone. If date_str parameter has no timezone, it will be
        considered as UTC. The result is in ISO format.
        """
        try:
            dt = parse_date_str_to_utc(date_str)
            result = dt.isoformat()
            logger.info("Converting date '%s' string to UTC", result)
            return result
        except dateutil.parser.ParserError as e:
            logger.error("Error converting date string to utc timezone: %s", e)
            return {
                'error': True,
                'error_message': f"Invalid date format: '{date_str}'",
            }

    @staticmethod
    def convert_datetime_to_local_timezone(date_str: str) -> str | dict:
        """
        Converts a date string to local timezone. If date_str parameter has no timezone, it will be
        considered as UTC. The result will be in ISO format.
        """
        try:
            dt = parse_date_str_to_utc(date_str)
            local_tz = ZoneInfo('localtime')
            result = dt.astimezone(local_tz).isoformat()
            logger.info("Converting date '%s' string to local timezone", result)
            return result
        except dateutil.parser.ParserError as e:
            logger.error("Error converting date string to local timezone: %s", e)
            return {
                'error': True,
                'error_message': f"Invalid date format: '{date_str}'",
            }

    @staticmethod
    def convert_datetime_to_timezone(date_str: str, timezone_str: str) -> str | dict:
        """
        Converts a date string to a specific timezone. If date_str parameter has no timezone, it will be
        considered as UTC. The result will be in ISO format.
        """
        try:
            dt = parse_date_str_to_utc(date_str)
            result = dt.astimezone(ZoneInfo(timezone_str)).isoformat()
            logger.info("Converted date '%s' string to timezone '%s'", result, timezone_str)
            return result
        except ZoneInfoNotFoundError as e:
            logger.error("Timezone not found: %s", e)
            return {
                'error': True,
                'error_message':f"Invalid timezone: '{timezone_str}'",
            }
        except dateutil.parser.ParserError as e:
            logger.error("Error converting date string to timezone '%s': Invalid datetime format: %s", timezone_str, date_str)
            return {
                'error': True,
                'error_message': f"Invalid date format: '{date_str}'",
            }

    @staticmethod
    def get_possible_datetime_timezones(date_str: str) -> list[str] | dict:
        """
        Returns a list of possible timezones for a given date string. The function uses dateutil.parser
        to handle various date formats.
        :param date_str: The date string to parse.
        :return: A list of possible timezones.
        """
        try:
            dt = dateutil.parser.parse(date_str, tzinfos=TZINFOS)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            target_offset = dt.utcoffset()
            result = []
            for zone_name in available_timezones():
                zone_dt = dt.astimezone(ZoneInfo(zone_name))
                if zone_dt.utcoffset() == target_offset:
                    result.append(zone_name)
            return result
        except dateutil.parser.ParserError as e:
            logger.error("Invalid datetime format: %s", date_str)
            return {
                'error': True,
                'error_message': f"Invalid date format: '{date_str}'",
            }
