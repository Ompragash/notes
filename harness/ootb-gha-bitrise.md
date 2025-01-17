## Steps to Update OOTB GitHub Action and BitRise Plugin Tool Version

1. Make Changes to the Plugin Repository:
- Apply the required changes or fixes to the Drone Plugin repository.
- Ensure all changes are committed and tested thoroughly.
2. Release a New Version:
- Tag the updated version in the Drone Plugin repository.
- Push the tag to trigger the release process.
- Verify that the new version of the plugin is successfully released.
3. Update the Runner Repository:
- Navigate to the Drone AWS Runner PR.
- Update the reference in the PR with the newly released plugin tag.
- Test the integration to confirm compatibility.
4. Final Review and Merge:
- Ensure all tests pass in the AWS Runner PR.
- Complete the review process and merge the changes.
