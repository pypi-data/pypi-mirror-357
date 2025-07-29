"""Profile management command for social media accounts."""

import typer
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import yaml

from ...core.profiles.generator import ProfileGenerator, ProfileContent

console = Console()

# Create profile app
profile_app = typer.Typer(name="profile", help="Generate and manage social media profiles")

@profile_app.command()
def generate(
    app_name: Optional[str] = typer.Option(None, "--app-name", "-n", help="Your app/product name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="App description"),
    github_url: Optional[str] = typer.Option(None, "--github-url", "-g", help="GitHub repository URL"),
    website_url: Optional[str] = typer.Option(None, "--website-url", "-w", help="Website URL"),
    platform: List[str] = typer.Option([], "--platform", "-P", help="Specific platforms (default: all)"),
    style: str = typer.Option('friendly', "--style", "-s", help="Profile style"),
    campaign_config: Optional[str] = typer.Option(None, "--campaign-config", "-c", help="Path to campaign.yaml")
):
    """Generate optimized social media profiles."""
    
    generator = ProfileGenerator()
    
    # Load campaign config if provided
    project_info = {}
    if campaign_config:
        try:
            with open(campaign_config, 'r', encoding='utf-8') as f:
                campaign_data = yaml.safe_load(f)
                project_info.update(campaign_data)
                console.print(f"✅ Loaded campaign config from {campaign_config}")
        except Exception as e:
            console.print(f"⚠️  Could not load campaign config: {e}")
    
    # Override with provided values
    if app_name:
        project_info["name"] = app_name
    if description:
        project_info["description"] = description
    if website_url:
        project_info["website_url"] = website_url
    if github_url:
        project_info["github_url"] = github_url
    
    # Set defaults if nothing provided
    if not project_info.get("name"):
        project_info["name"] = "AetherPost"
    if not project_info.get("description"):
        project_info["description"] = "Social media automation for developers"
    
    # Determine platforms to generate
    if not platform:
        platforms = ["twitter", "bluesky", "instagram", "github"]
    else:
        platforms = platform
    
    console.print(Panel(
        f"[bold green]Generating profiles for {project_info.get('name', 'your app')}[/bold green]",
        title="🎭 Profile Generation"
    ))
    
    # Generate profiles for each platform
    for platform_name in platforms:
        try:
            console.print(f"\n[bold blue]━━━ {platform_name.title()} Profile ━━━[/bold blue]")
            
            profile = generator.generate_profile(platform_name, project_info, style)
            
            # Display the generated profile
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("Field", style="cyan", width=15)
            table.add_column("Value", style="white")
            
            table.add_row("Display Name", profile.display_name)
            table.add_row("Bio", profile.bio)
            if profile.website_url:
                table.add_row("Website", profile.website_url)
            
            table.add_row("Characters", f"{profile.character_count}/{profile.character_limit}")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"❌ Error generating {platform_name} profile: {e}")

@profile_app.command()
def platforms():
    """Show supported platforms and their requirements."""
    
    generator = ProfileGenerator()
    
    console.print(Panel(
        "[bold green]Supported Social Media Platforms[/bold green]",
        title="📱 Platform Support"
    ))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Platform", style="cyan")
    table.add_column("Bio Limit")
    table.add_column("Features")
    
    platforms = generator.get_supported_platforms()
    for platform_name in platforms:
        config = generator.get_platform_requirements(platform_name)
        if config:
            features = []
            if config.supports_website:
                features.append("Website")
            if config.supports_location:
                features.append("Location")
            if config.emoji_friendly:
                features.append("Emoji")
            
            table.add_row(
                platform_name.title(),
                str(config.bio_max_length),
                ", ".join(features)
            )
    
    console.print(table)

@profile_app.command()
def demo():
    """Show profile generation demo with sample data."""
    
    console.print(Panel(
        "[bold green]AetherPost Profile Generator Demo[/bold green]\n"
        "This demo shows how to generate optimized profiles for your app.",
        title="🎭 Profile Demo"
    ))
    
    # Sample project data
    demo_data = {
        "name": "MyAwesomeApp",
        "description": "Revolutionary productivity tool for developers",
        "urls": {
            "main": "https://myapp.example.com",
            "github": "https://github.com/user/myawesomeapp",
            "docs": "https://docs.myapp.example.com"
        },
        "tech_stack": ["Python", "FastAPI", "React"],
        "features": ["automation", "developer-tools", "productivity"]
    }
    
    generator = ProfileGenerator()
    
    # Show profiles for major platforms
    demo_platforms = ["twitter", "bluesky"]
    
    for platform in demo_platforms:
        console.print(f"\n[bold blue]━━━ {platform.title()} Profile ━━━[/bold blue]")
        
        profile = generator.generate_profile(platform, demo_data)
        
        # Display the generated profile
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="cyan", width=15)
        table.add_column("Value", style="white")
        
        table.add_row("Display Name", profile.display_name)
        table.add_row("Bio", profile.bio)
        if profile.website_url:
            table.add_row("Website", profile.website_url)
        
        table.add_row("Characters", f"{profile.character_count}/{profile.character_limit}")
        
        console.print(table)
        
        if profile.additional_links:
            console.print("\n[dim]Additional URLs:[/dim]")
            for link in profile.additional_links:
                console.print(f"  • {link['title']}: {link['url']}")

@profile_app.command()
def update(
    platform: str = typer.Argument(..., help="Platform to update (twitter, bluesky)"),
    campaign_config: Optional[str] = typer.Option("campaign.yaml", "--config", "-c", help="Path to campaign.yaml")
):
    """Update social media profile with generated content."""
    from ...core.connector_factory import get_connector
    from ...core.common.config_manager import config_manager
    
    try:
        # Load campaign config
        with open(campaign_config, 'r', encoding='utf-8') as f:
            campaign_data = yaml.safe_load(f)
        
        # Generate profile content
        generator = ProfileGenerator()
        profile = generator.generate_profile(platform, campaign_data, campaign_data.get('content', {}).get('style', 'friendly'))
        
        console.print(f"[bold blue]Updating {platform.title()} profile...[/bold blue]")
        console.print(f"Display Name: [green]{profile.display_name}[/green]")
        console.print(f"Bio: [green]{profile.bio}[/green]")
        if profile.website_url:
            console.print(f"Website: [green]{profile.website_url}[/green]")
        
        # Get connector and update profile
        connector = get_connector(platform)
        
        if platform == "twitter":
            success = _update_twitter_profile(connector, profile)
        elif platform == "bluesky":
            success = _update_bluesky_profile(connector, profile)
        else:
            console.print(f"❌ Platform {platform} not supported for profile updates")
            return
            
        if success:
            console.print(f"✅ Successfully updated {platform.title()} profile!")
        else:
            console.print(f"❌ Failed to update {platform.title()} profile")
            
    except Exception as e:
        console.print(f"❌ Error updating profile: {e}")

@profile_app.command()
def upload_avatar(
    platform: str = typer.Argument(..., help="Platform to update (twitter, bluesky)"),
    generate: bool = typer.Option(False, "--generate", "-g", help="Generate AI avatar"),
    image_path: Optional[str] = typer.Option(None, "--image", "-i", help="Path to image file"),
    campaign_config: Optional[str] = typer.Option("campaign.yaml", "--config", "-c", help="Path to campaign.yaml")
):
    """Upload avatar to social media platform."""
    from ...core.connector_factory import get_connector
    from ...core.media.image_generator import ImageGenerator
    
    try:
        # Load campaign config for context
        with open(campaign_config, 'r', encoding='utf-8') as f:
            campaign_data = yaml.safe_load(f)
        
        image_data = None
        
        if generate:
            console.print("[bold blue]Generating AI avatar...[/bold blue]")
            generator = ImageGenerator()
            
            # Create avatar prompt based on campaign
            prompt = f"Professional logo for {campaign_data.get('name', 'AetherPost')}: {campaign_data.get('description', 'social media automation tool')}. Modern, clean, tech-focused design."
            
            image_data = generator.generate_avatar(prompt)
            console.print("✅ Avatar generated successfully!")
            
        elif image_path:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            console.print(f"✅ Loaded image from {image_path}")
        else:
            console.print("❌ Must specify either --generate or --image")
            return
        
        # Get connector and upload avatar
        connector = get_connector(platform)
        
        console.print(f"[bold blue]Uploading avatar to {platform.title()}...[/bold blue]")
        
        if platform == "twitter":
            success = _upload_twitter_avatar(connector, image_data)
        elif platform == "bluesky":
            success = _upload_bluesky_avatar(connector, image_data)
        else:
            console.print(f"❌ Platform {platform} not supported for avatar uploads")
            return
            
        if success:
            console.print(f"✅ Successfully uploaded avatar to {platform.title()}!")
        else:
            console.print(f"❌ Failed to upload avatar to {platform.title()}")
            
    except Exception as e:
        console.print(f"❌ Error uploading avatar: {e}")

@profile_app.command()
def show(
    platform: str = typer.Argument(..., help="Platform to show (twitter, bluesky)")
):
    """Show current social media profile."""
    from ...core.connector_factory import get_connector
    
    try:
        console.print(f"[bold blue]Fetching {platform.title()} profile...[/bold blue]")
        
        connector = get_connector(platform)
        
        if platform == "twitter":
            profile_info = _get_twitter_profile(connector)
        elif platform == "bluesky":
            profile_info = _get_bluesky_profile(connector)
        else:
            console.print(f"❌ Platform {platform} not supported")
            return
            
        if profile_info:
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("Field", style="cyan", width=15)
            table.add_column("Value", style="white")
            
            for key, value in profile_info.items():
                table.add_row(key.title(), str(value))
            
            console.print(table)
        else:
            console.print(f"❌ Could not fetch {platform.title()} profile")
            
    except Exception as e:
        console.print(f"❌ Error fetching profile: {e}")

# Helper functions for platform-specific operations
def _update_twitter_profile(connector, profile: ProfileContent) -> bool:
    """Update Twitter profile."""
    if hasattr(connector, 'api') and connector.api:
        try:
            update_params = {}
            if profile.display_name:
                update_params['name'] = profile.display_name
            if profile.bio:
                bio_text = profile.bio[:160] if len(profile.bio) > 160 else profile.bio
                update_params['description'] = bio_text
            if profile.website_url:
                update_params['url'] = profile.website_url
                
            connector.api.update_profile(**update_params)
            return True
        except Exception as e:
            console.print(f"Twitter API error: {e}")
            return False
    return False

def _update_bluesky_profile(connector, profile: ProfileContent) -> bool:
    """Update Bluesky profile."""
    if hasattr(connector, 'client') and connector.client:
        try:
            # Get current profile
            current_profile = connector.client.com.atproto.repo.describe_repo()
            
            # Update profile record
            profile_record = {
                'displayName': profile.display_name,
                'description': profile.bio[:256] if len(profile.bio) > 256 else profile.bio,
            }
            
            if profile.website_url:
                profile_record['website'] = profile.website_url
            
            # Put updated profile
            connector.client.com.atproto.repo.put_record({
                'repo': connector.client.me.did,
                'collection': 'app.bsky.actor.profile',
                'rkey': 'self',
                'record': profile_record
            })
            return True
        except Exception as e:
            console.print(f"Bluesky API error: {e}")
            return False
    return False

def _upload_twitter_avatar(connector, image_data: bytes) -> bool:
    """Upload avatar to Twitter."""
    try:
        connector.api.update_profile_image(image_data)
        return True
    except Exception as e:
        console.print(f"Twitter avatar upload error: {e}")
        return False

def _upload_bluesky_avatar(connector, image_data: bytes) -> bool:
    """Upload avatar to Bluesky."""
    try:
        # Upload blob first
        blob_response = connector.client.com.atproto.repo.upload_blob(image_data)
        
        # Get current profile
        current_profile = connector.client.com.atproto.repo.get_record({
            'repo': connector.client.me.did,
            'collection': 'app.bsky.actor.profile',
            'rkey': 'self'
        })
        
        # Update profile with new avatar
        profile_record = current_profile.value
        profile_record['avatar'] = blob_response.blob
        
        connector.client.com.atproto.repo.put_record({
            'repo': connector.client.me.did,
            'collection': 'app.bsky.actor.profile',
            'rkey': 'self',
            'record': profile_record
        })
        return True
    except Exception as e:
        console.print(f"Bluesky avatar upload error: {e}")
        return False

def _get_twitter_profile(connector) -> dict:
    """Get current Twitter profile."""
    try:
        me = connector.api.verify_credentials()
        return {
            'name': me.name,
            'screen_name': f"@{me.screen_name}",
            'description': me.description,
            'url': me.url,
            'followers_count': me.followers_count,
            'friends_count': me.friends_count
        }
    except Exception as e:
        console.print(f"Twitter profile fetch error: {e}")
        return None

def _get_bluesky_profile(connector) -> dict:
    """Get current Bluesky profile."""
    try:
        profile = connector.client.get_profile(connector.client.me.handle)
        return {
            'display_name': profile.display_name,
            'handle': profile.handle,
            'description': profile.description,
            'followers_count': profile.followers_count,
            'follows_count': profile.follows_count
        }
    except Exception as e:
        console.print(f"Bluesky profile fetch error: {e}")
        return None