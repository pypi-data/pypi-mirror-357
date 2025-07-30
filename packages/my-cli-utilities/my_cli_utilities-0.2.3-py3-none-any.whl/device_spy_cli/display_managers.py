# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Callable
import typer
from my_cli_utilities_common.pagination import paginated_display
from my_cli_utilities_common.config import BaseConfig
from wcwidth import wcswidth
# Jenkins helper will be imported inside the method to avoid import issues


class Config(BaseConfig):
    pass


class BaseDisplayManager:
    """Base class for display managers with common utilities."""
    
    @staticmethod
    def _get_aligned_text(label: str, value: Any, width: int = 18) -> str:
        """Aligns text by calculating display width, not character length."""
        padding = " " * (width - wcswidth(label))
        return f"{label}{padding}{value}"
    
    @staticmethod
    def get_safe_value(data: Dict, key: str, default: str = "N/A") -> str:
        """Safely get value from dictionary with default."""
        return str(data.get(key, default) or default)
    
    @staticmethod
    def format_percentage(current: int, total: int) -> str:
        """Format percentage with proper handling of division by zero."""
        if total == 0:
            return "N/A"
        return f"{round((current / total) * 100, 1)}%"
    
    @staticmethod
    def truncate_udid(udid: str, length: int = 8) -> str:
        """Truncate UDID for better readability."""
        return f"{udid[:length]}..." if len(udid) > length else udid


class DeviceDisplayManager(BaseDisplayManager):
    """Handles device information display."""
    
    @staticmethod
    def display_device_info(device: Dict) -> None:
        """Display device information in a user-friendly format."""
        typer.echo(f"\n📱 Device Information")
        typer.echo("=" * Config.DISPLAY_WIDTH)
        
        # Extract key information using safe getter
        fields = [
            ("📋 UDID:", "udid"),
            ("🔧 Platform:", "platform"),
            ("📟 Model:", "model"),
            ("🎯 OS Version:", "platform_version"),
            ("🖥️  Host:", "hostname"),
        ]
        
        for label, key in fields:
            value = BaseDisplayManager.get_safe_value(device, key)
            typer.echo(f"{label:<18} {value}")
        
        # Optional fields
        optional_fields = [
            ("🌐 Host IP:", "host_ip"),
            ("📍 Location:", "location"),
            ("🌐 IP:Port:", "ip_port"),
        ]
        
        for label, key in optional_fields:
            value = device.get(key)
            if value and value != "N/A":
                typer.echo(f"{label:<18} {value}")
        
        # Status
        is_locked = device.get("is_locked", False)
        status = "🔒 Locked" if is_locked else "✅ Available"
        typer.echo(f"{'🔐 Status:':<18} {status}")
        typer.echo("=" * Config.DISPLAY_WIDTH)

    @staticmethod
    def display_device_list(devices: List[Dict], title: str) -> None:
        """Display a list of devices with pagination."""
        def display_device(device: Dict, index: int) -> None:
            model = BaseDisplayManager.get_safe_value(device, "model")
            os_version = BaseDisplayManager.get_safe_value(device, "platform_version")
            udid = BaseDisplayManager.get_safe_value(device, "udid")
            hostname = BaseDisplayManager.get_safe_value(device, "hostname")
            
            typer.echo(f"\n{index}. {model} ({os_version})")
            typer.echo(f"   UDID: {udid}")
            typer.echo(f"   Host: {hostname}")
        
        paginated_display(devices, display_device, title, Config.PAGE_SIZE, Config.DISPLAY_WIDTH)
        
        typer.echo("\n" + "=" * Config.DISPLAY_WIDTH)
        typer.echo(f"💡 Use 'ds udid <udid>' to get detailed information")
        typer.echo("=" * Config.DISPLAY_WIDTH)


class HostDisplayManager(BaseDisplayManager):
    """Handles host information display."""
    
    @staticmethod
    def display_host_results(hosts: List[Dict], query: str) -> None:
        """Display host search results."""
        typer.echo(f"\n🔍 Host Search Results for: '{query}'")
        typer.echo("=" * Config.DISPLAY_WIDTH)
        
        for i, host in enumerate(hosts, 1):
            hostname = BaseDisplayManager.get_safe_value(host, "hostname")
            alias = BaseDisplayManager.get_safe_value(host, "alias")
            typer.echo(f"{i}. {alias} ({hostname})")
        
        typer.echo("=" * Config.DISPLAY_WIDTH)

    @staticmethod
    def display_detailed_host_info(host: Dict, devices: List[Dict]) -> None:
        """Display comprehensive host information."""
        hostname = BaseDisplayManager.get_safe_value(host, "hostname")
        alias = BaseDisplayManager.get_safe_value(host, "alias")
        
        typer.echo(f"\n🖥️  Host Information: {alias}")
        typer.echo("=" * Config.DISPLAY_WIDTH)
        
        HostDisplayManager._display_basic_info(host)
        HostDisplayManager._display_configuration(host)
        HostDisplayManager._display_jenkins_info(alias, hostname)  # Use alias as primary parameter
        HostDisplayManager._display_device_statistics(host, devices)
        HostDisplayManager._display_device_details(devices)
        HostDisplayManager._display_usage_tips(alias)

    @staticmethod
    def _display_basic_info(host: Dict) -> None:
        """Display basic host information with perfect text alignment."""
        
        alias = BaseDisplayManager.get_safe_value(host, "alias")
        hostname = BaseDisplayManager.get_safe_value(host, "hostname")
        platform = f"{host.get('platform', 'N/A')} {host.get('version', '')}".strip()
        
        # Use simple text labels for perfect alignment
        typer.echo(f"Alias:        {alias}")
        typer.echo(f"Hostname:     {hostname}")
        typer.echo(f"Platform:     {platform}")
        
        # Optional description
        remark = host.get("remark")
        if remark and remark != "N/A":
            typer.echo(f"Description:  {remark}")
        
        # SSH status
        ssh_status = host.get("ssh_status", False)
        ssh_icon = "✅" if ssh_status else "❌"
        ssh_text = "Connected" if ssh_status else "Disconnected"
        typer.echo(f"SSH Status:   {ssh_icon} {ssh_text}")

    @staticmethod
    def _display_jenkins_info(alias: str, hostname: str) -> None:
        """Display Jenkins integration information with clean text alignment."""
        typer.echo(f"\nJenkins Integration:")

        try:
            # Use jenkins_helpers module to get Jenkins information
            from my_cli_utilities_common.jenkins_helpers import get_jenkins_info_for_host
            
            # Prefer alias, if alias is not XMNA format, use hostname
            jenkins_host = alias if alias.upper().startswith('XMNA') else hostname
            jenkins_info = get_jenkins_info_for_host(jenkins_host)
            
            if not jenkins_info:
                typer.echo(f"   ❌ No Jenkins agent found for {jenkins_host}")
                return
            
            if 'error' in jenkins_info:
                typer.echo(f"   ⚠️  {jenkins_info['error']}")
                return
                
        except ImportError:
            typer.echo(f"   ⚠️  Jenkins integration not available")
            return
        except Exception as e:
            typer.echo(f"   ❌ Error fetching Jenkins info: {e}")
            return
        
        # Display Jenkins information
        HostDisplayManager._render_jenkins_status(jenkins_info)

    @staticmethod
    def _render_jenkins_status(jenkins_info: Dict) -> None:
        """Render Jenkins status information"""
        # Online status
        online_status = jenkins_info.get('online', False)
        status_icon = "🟢" if online_status else "🔴"
        status_text = "Online" if online_status else "Offline"
        typer.echo(f"   Status:       {status_icon} {status_text}")
        
        # Label information
        labels = jenkins_info.get('labels', [])
        labels_text = ", ".join(labels) if labels else "No labels assigned"
        typer.echo(f"   Labels:       {labels_text}")
        
        # Executor status
        total_executors = jenkins_info.get('total_executors', 0)
        if total_executors > 0:
            busy_executors = jenkins_info.get('busy_executors', 0)
            idle_executors = total_executors - busy_executors
            executors_text = f"{total_executors} total ({busy_executors} busy, {idle_executors} idle)"
            typer.echo(f"   Executors:    {executors_text}")
            
            # Display running jobs
            executors = jenkins_info.get('executors', [])
            HostDisplayManager._display_running_jobs(executors)
        else:
            typer.echo(f"   Executors:    No executor information available")
        
        # Jenkins URL
        jenkins_url = jenkins_info.get('jenkins_url', '')
        if jenkins_url:
            typer.echo(f"   Jenkins URL:  {jenkins_url}")

    @staticmethod
    def _display_running_jobs(executors: List[Dict]) -> None:
        """Display currently running jobs on executors."""
        running_jobs = [e for e in executors if not e.get('idle', True)]
        
        if not running_jobs:
            return
        
        typer.echo(f"   Running Jobs:")
        for executor in running_jobs:
            executor_num = executor.get('number', 0)
            current_job = executor.get('current_executable')  # Note: use current_executable, not currentExecutable
            
            if current_job:
                job_name = current_job.get('display_name', 'Unknown Job')
                job_number = current_job.get('number', 'N/A')
                progress = executor.get('progress', -1)
                
                progress_text = ""
                if progress >= 0:
                    progress_text = f" ({progress}%)"
                
                # Display executor number +1 for better user experience (start from 1 instead of 0)
                typer.echo(f"      Executor {executor_num + 1}: {job_name} #{job_number}{progress_text}")
            else:
                typer.echo(f"      Executor {executor_num + 1}: Running (details unavailable)")

    @staticmethod
    def _display_configuration(host: Dict) -> None:
        """Display host configuration information."""
        typer.echo(f"\n⚙️  Host Configuration:")
        
        config_fields = [
            ("📱 iOS Capacity:", "default_ios_devices_amount", "devices"),
            ("🤖 Android Cap.:", "default_android_devices_amount", "devices"),
            ("🚀 Appium Count:", "appium_count", "instances"),
            ("📱 iOS Sim Max:", "max_ios_simulator_concurrency", "concurrent"),
        ]
        
        for label, key, unit in config_fields:
            value = host.get(key, 0)
            typer.echo(f"   {label:<16} {value} {unit}")

    @staticmethod
    def _display_device_statistics(host: Dict, devices: List[Dict]) -> None:
        """Display device statistics and utilization."""
        # API statistics
        api_stats = {
            "total": host.get("device_count", 0),
            "ios": host.get("ios_device_count", 0),
            "android": host.get("android_device_count", 0),
        }
        
        # Real device analysis
        device_analysis = HostDisplayManager._analyze_devices(devices)
        
        typer.echo(f"\n📊 Device Statistics:")
        typer.echo(f"   📈 API Reported:   {api_stats['total']} total ({api_stats['ios']} iOS, {api_stats['android']} Android)")
        typer.echo(f"   🔍 Live Status:    {device_analysis['total']} total ({device_analysis['ios']} iOS, {device_analysis['android']} Android)")
        typer.echo(f"   🔒 Locked:         {device_analysis['locked']} devices")
        typer.echo(f"   ✅ Available:      {device_analysis['available']} devices")
        
        # Utilization analysis
        HostDisplayManager._display_utilization(host, device_analysis)

    @staticmethod
    def _analyze_devices(devices: List[Dict]) -> Dict[str, int]:
        """Analyze device statistics."""
        android_devices = [d for d in devices if d.get("platform") == "android"]
        ios_devices = [d for d in devices if d.get("platform") == "ios"]
        locked_devices = [d for d in devices if d.get("is_locked", False)]
        available_devices = [d for d in devices if not d.get("is_locked", False)]
        
        return {
            "total": len(devices),
            "android": len(android_devices),
            "ios": len(ios_devices),
            "locked": len(locked_devices),
            "available": len(available_devices),
            "android_devices": android_devices,
            "ios_devices": ios_devices,
        }

    @staticmethod
    def _display_utilization(host: Dict, analysis: Dict[str, int]) -> None:
        """Display utilization percentages."""
        default_ios = host.get("default_ios_devices_amount", 0)
        default_android = host.get("default_android_devices_amount", 0)
        
        if default_ios > 0:
            ios_utilization = BaseDisplayManager.format_percentage(analysis["ios"], default_ios)
            typer.echo(f"   📱 iOS Usage:      {ios_utilization} ({analysis['ios']}/{default_ios})")
        
        if default_android > 0:
            android_utilization = BaseDisplayManager.format_percentage(analysis["android"], default_android)
            typer.echo(f"   🤖 Android Usage:  {android_utilization} ({analysis['android']}/{default_android})")

    @staticmethod
    def _display_device_details(devices: List[Dict]) -> None:
        """Display detailed device list."""
        if not devices:
            return
            
        typer.echo(f"\n📋 Connected Device Details:")
        typer.echo("-" * Config.DISPLAY_WIDTH)
        
        analysis = HostDisplayManager._analyze_devices(devices)
        
        for platform in ["android", "ios"]:
            platform_devices = analysis.get(f"{platform}_devices", [])
            if platform_devices:
                HostDisplayManager._display_platform_devices(platform, platform_devices)

    @staticmethod
    def _display_platform_devices(platform: str, devices: List[Dict]) -> None:
        """Display devices for a specific platform with full UDID."""
        platform_emoji = "🤖" if platform == "android" else "🍎"
        platform_name = platform.capitalize()
        
        typer.echo(f"\n{platform_emoji} {platform_name} Devices ({len(devices)}):")
        
        max_display = 8
        for i, device in enumerate(devices[:max_display], 1):
            model = BaseDisplayManager.get_safe_value(device, "model")
            os_version = BaseDisplayManager.get_safe_value(device, "platform_version")
            udid = BaseDisplayManager.get_safe_value(device, "udid")
            status = "🔒" if device.get("is_locked", False) else "✅"
            
            typer.echo(f"   {i}. {status} {model} ({os_version})")
            typer.echo(f"      UDID: {udid}")  # Show full UDID instead of truncated
        
        if len(devices) > max_display:
            remaining = len(devices) - max_display
            typer.echo(f"   ... and {remaining} more {platform} devices")

    @staticmethod
    def _display_usage_tips(alias: str) -> None:
        """Display usage tips and suggestions."""
        typer.echo("=" * Config.DISPLAY_WIDTH)
        typer.echo(f"💡 Use 'ds devices android' or 'ds devices ios' to see all available devices")
        typer.echo(f"💡 Use 'ds ssh {alias}' to connect to this host")
        typer.echo("=" * Config.DISPLAY_WIDTH) 